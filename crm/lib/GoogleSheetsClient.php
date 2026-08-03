<?php
/**
 * Lightweight Google Sheets client for PHP (zero dependencies).
 * Uses JWT-based service account authentication via cURL.
 * No composer required.
 */

class GoogleSheetsClient
{
    private string $access_token = '';
    private string $sheet_id;

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
            'scope' => 'https://www.googleapis.com/auth/spreadsheets.readonly',
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

    /**
     * Read all rows from the first tab of the sheet.
     * Returns [header, rows] where rows is [col1, col2, ...]
     */
    public function read_sheet(string $range = 'A1:ZZ'): array
    {
        $url = "https://sheets.googleapis.com/v4/spreadsheets/{$this->sheet_id}/values/$range";
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_HTTPHEADER     => ["Authorization: Bearer {$this->access_token}"],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 30,
        ]);
        $resp = json_decode(curl_exec($ch), true);
        curl_close($ch);

        $values = $resp['values'] ?? [];
        if (empty($values)) {
            return [[], []];
        }
        $header = $values[0];
        $rows = array_slice($values, 1);
        return [$header, $rows];
    }
}

function base64url_encode(string $data): string
{
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}
