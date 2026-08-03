<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Google Sheets Sync Client
 * Uses JWT-based service account authentication via cURL.
 * No composer required.
 * 
 * Supports both read and write operations.
 */

class GoogleSheetsClient
{
    private string $access_token = '';
    private string $sheet_id;
    private array $header_cache = [];

    public function __construct(string $service_account_json_path, string $sheet_id)
    {
        $this->sheet_id = $sheet_id;

        if (!file_exists($service_account_json_path)) {
            throw new RuntimeException("Service account file not found: $service_account_json_path");
        }
        $sa = json_decode(file_get_contents($service_account_json_path), true);
        if (!$sa || empty($sa['client_email']) || empty($sa['private_key'])) {
            throw new RuntimeException("Invalid service account JSON");
        }
        $this->access_token = $this->get_jwt_token($sa);
    }

    private function get_jwt_token(array $sa): string
    {
        $now = time();
        $header = base64url_encode(json_encode([
            'alg' => 'RS256',
            'typ' => 'JWT',
            'kid' => $sa['private_key_id'] ?? '',
        ]));
        $payload = base64url_encode(json_encode([
            'iss'   => $sa['client_email'],
            'scope' => 'https://www.googleapis.com/auth/spreadsheets',
            'aud'   => 'https://oauth2.googleapis.com/token',
            'exp'   => $now + 3600,
            'iat'   => $now,
        ]));
        $signature = '';
        openssl_sign("$header.$payload", $signature, $sa['private_key'], 'sha256WithRSAEncryption');
        $jwt = "$header.$payload." . base64url_encode($signature);

        // Exchange JWT for access token
        $ch = curl_init('https://oauth2.googleapis.com/token');
        curl_setopt_array($ch, [
            CURLOPT_POST       => true,
            CURLOPT_POSTFIELDS => http_build_query([
                'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion'  => $jwt,
            ]),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 10,
        ]);
        $resp = json_decode(curl_exec($ch), true);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($code !== 200 || empty($resp['access_token'])) {
            throw new RuntimeException("Failed to get access token: " . ($resp['error_description'] ?? 'unknown'));
        }
        return $resp['access_token'];
    }

    private function api_call(string $method, string $endpoint, array $body = []): array
    {
        $url = "https://sheets.googleapis.com/v4/spreadsheets/{$this->sheet_id}/$endpoint";
        $ch = curl_init($url);
        $opts = [
            CURLOPT_HTTPHEADER => [
                "Authorization: Bearer {$this->access_token}",
                "Content-Type: application/json",
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 30,
            CURLOPT_CUSTOMREQUEST  => $method,
        ];
        if (!empty($body)) {
            $opts[CURLOPT_POSTFIELDS] = json_encode($body);
        }
        curl_setopt_array($ch, $opts);
        $resp = json_decode(curl_exec($ch), true);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($code >= 400) {
            $err = $resp['error']['message'] ?? json_encode($resp);
            throw new RuntimeException("Google Sheets API error ($code): $err");
        }
        return $resp ?? [];
    }

    /**
     * Read all rows from the specified range.
     * Returns [header, rows] where rows is [col1, col2, ...]
     */
    public function read_sheet(string $range = 'A1:ZZ'): array
    {
        $resp = $this->api_call('GET', "values/$range");
        $values = $resp['values'] ?? [];
        if (empty($values)) {
            return [[], []];
        }
        $header = $values[0];
        $rows = array_slice($values, 1);
        $this->header_cache = $header;
        return [$header, $rows];
    }

    /**
     * Find the row number (1-indexed) of a lead by lead_key in column A.
     * Returns null if not found.
     */
    public function find_row(string $lead_key): ?int
    {
        $resp = $this->api_call('GET', 'values/A:A');
        $values = $resp['values'] ?? [];
        foreach ($values as $i => $cell) {
            if (($cell[0] ?? '') === $lead_key) {
                return $i + 1; // 1-indexed for Sheets API
            }
        }
        return null;
    }

    /**
     * Get the header row and build a column map.
     * Returns [header_array, col_name_to_index_map]
     */
    public function get_header(): array
    {
        if (!empty($this->header_cache)) {
            $header = $this->header_cache;
        } else {
            $resp = $this->api_call('GET', 'values/1:1');
            $header = $resp['values'][0] ?? [];
            $this->header_cache = $header;
        }
        $col_map = [];
        foreach ($header as $i => $name) {
            $col_map[$name] = $i; // 0-indexed
        }
        return [$header, $col_map];
    }

    /**
     * Update a single cell by row and column (e.g. "D5").
     */
    public function update_cell(string $cell_ref, string $value): void
    {
        $this->api_call('PUT', "values/$cell_ref", [
            'values' => [[$value]],
            'majorDimension' => 'ROWS',
        ]);
    }

    /**
     * Update one or more fields for a lead identified by lead_key.
     *
     * @param string $lead_key  The lead_key to find
     * @param array  $fields    Associative array of {column_name: value}
     * @return int              Number of fields updated (0 if lead not found)
     */
    public function update_lead_fields(string $lead_key, array $fields): int
    {
        $row = $this->find_row($lead_key);
        if ($row === null) {
            return 0;
        }

        [$header, $col_map] = $this->get_header();
        $updated = 0;

        foreach ($fields as $col_name => $value) {
            if (!isset($col_map[$col_name])) {
                continue; // column doesn't exist in sheet
            }
            $col_letter = $this->column_letter($col_map[$col_name] + 1); // 1-indexed
            $cell_ref = $col_letter . $row;
            try {
                $this->update_cell($cell_ref, (string)$value);
                $updated++;
            } catch (RuntimeException $e) {
                error_log("Sheets write-back: $col_name for $lead_key: " . $e->getMessage());
            }
        }
        return $updated;
    }

    /**
     * Update a full row of values for a lead (all columns).
     */
    public function update_row(string $lead_key, array $row_values): bool
    {
        $row = $this->find_row($lead_key);
        if ($row === null) {
            return false;
        }

        $range = "A$row:" . $this->column_letter(count($row_values)) . $row;
        $this->api_call('PUT', "values/$range", [
            'values' => [$row_values],
            'majorDimension' => 'ROWS',
        ]);
        return true;
    }

    /**
     * Append a new row to the sheet.
     */
    public function append_row(array $values): void
    {
        $this->api_call('POST', 'values/A:ZZ:append?valueInputOption=RAW', [
            'values' => [$values],
            'majorDimension' => 'ROWS',
        ]);
    }

    private function column_letter(int $index): string
    {
        $letter = '';
        while ($index > 0) {
            $mod = ($index - 1) % 26;
            $letter = chr(65 + $mod) . $letter;
            $index = (int)(($index - $mod) / 26);
        }
        return $letter;
    }
}

function base64url_encode(string $data): string
{
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}