<?php
/**
 * TEMP maintenance: write Google service-account JSON + update config.local.php
 * DELETED after use. Not committed.
 */
$sa_json = <<<'JSON'
{
  "type": "service_account",
  "project_id": "gmp-demo-project-034017463",
  "private_key_id": "75e02b7eb9dd7b8577b90c503455c0458575ddcf",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCzvJWxY8YfEQ/o\nN8+K7CCj52H+Fk0n0cH2FZvjXFs/B6MsFc4efr3FWiA+UsI0kwejbUeaeY8d5QED\nfAwWgGvegSMWzCtoC3RLsNaAIA3ZPQXUR8AIz/SQNxVyemZuna51Dsg2z2pZ/Zdr\n5m77j6HPDTG/WrtLJNf8rFJgPHvcM6gxJoFInVAgQP8ZLEnx27M0Pe7iqtHK7JbO\n4D0hnc7Nk0VhprJ4xm5e+PgvkevX2wE3EerFSJYxaTZm3i3Ado79OZJPb0HJp6YG\npz0K0XIu+VyIiZvE0W5mbHgWuHq/0v7erySLbqOGFISav3guq1fuzP5mu/LGC0Ct\nOom+H18jAgMBAAECggEACIFO0ntJySqOub36WjT2QaTiippJKGGd1grYh5e7nm3t\nsL/1zJRrknn2g9YStPFhySZgq9SlixQzfUcfcBxZMZXWyggufaWDguY2IELKccWY\nQwVQkJowLnema8MsmbHO3mDGsW4U0ESJwWQnS39U3tSQm0d5DJzZUG5iSR+GyB96\nHifMJcRjb95g5Yh/HwTmLNCZcLIue4WESoXY8xDCRY+gwPi9c1ttWs33+CXuSekO\n6oqCfVrqAETuU+xKm/1+jlAslZBY/hnIDFj/q1kGZ5d7XuaTj5Ap3N0ZQWh2fDoI\nwC4NBr/h1wtbTKwXHSHvzJXm4vv4+JFxcTl38Qm5MQKBgQDjWadiz1CvgvailsMT\nqyFeSEhWpQAYTv5m0ADkEa/oWgfFRlMqX0Y4N/FQo7s6QjFgc/jhYU46xo+RQGgh\nWARTvyyUZgSGRdEikF4rwQaaw8vBeXaZhKaBDdQG7rSHqtLn3UQo621lFGRnp/h7\nDJb9cXUOJKc5EJ6CMplJOUFqlwKBgQDKYulqr4oCoMXS9SNBehJLzIbkcSR4GNbK\nyaI01J4MO3P/YV6O7TcdGsT9hPIhPJBdqqUNoNDnnpSvJpM6DPlE3e/T3dlmnjCL\nm3HpReefM52gm4sg6grpoQ9V1yQWF3/+H8uySeoD/TqAmUdi3T8Jaq3doMajV8fH\nJBwWWCc9VQKBgHu+dZwTiTAukT2H36AZ+iyOHUmDv5x7in69Ym7ArcVDE42trGCY\nwOiikmc45xRbqPJ9zQ4nX2QgZU5DByp29Mv8dzBCot3OrHkqqQcZphWg0ot5KDOA\n/vupYilvzbU2JltrlMjM85sb0VaWF2oqPRivo23SR26I/C2TitlPH6r7AoGAUkh2\nqAZocPsWktdRlyxfRewIp9YMQruukFH8HciX3VdKqPjYbfmp365jisNDghnShBJ9\n+pV4ecLypmdjkkV2DvbAq/3VhrAoAoqXfIUMT6C3pHW40g/1kdkGmBrZNBYn1pTs\nxzbf6vFImMI40Mws9dImkCXuvLhSo/ddaAQ9J+UCgYB/KiHrBaf132jgFV04sv/+\nxbTjj83tqqDJf3SvTbgZycVTrBDwfTTvieFTn4Ptnmbe03/IeDo8xsx0VS4PKglz\n7UYoe61iwAZ39gkw2qLJxcIq0D8OwG1xyMNX5+e+757ACAs0iLxhSrdtj0ERYT48\nxlCbNqzJPLtiwBGNi5v73Q==\n-----END PRIVATE KEY-----\n",
  "client_email": "tkvibes-datarequests@gmp-demo-project-034017463.iam.gserviceaccount.com",
  "client_id": "104547651405362307224",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tkvibes-datarequests%40gmp-demo-project-034017463.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
JSON;
$sheet_id = '1cZ7w4HlN5aGaSAY-m-9EPexqEaCVC52kRELPk1OGiXc';

$dir = __DIR__ . '/credentials';
if (!is_dir($dir)) mkdir($dir, 0755, true);
$sa_path = $dir . '/google-service-account.json';
file_put_contents($sa_path, $sa_json);
echo "wrote SA json: " . (file_exists($sa_path) ? 'ok ' . filesize($sa_path) . 'B' : 'FAILED') . "\n";

$cfg_file = __DIR__ . '/config.local.php';
$cfg = require $cfg_file;
$cfg['google_service_account'] = $sa_path;
$cfg['google_sheet_id'] = $sheet_id;
$out = '<?php' . PHP_EOL . 'return ' . var_export($cfg, true) . ';' . PHP_EOL;
file_put_contents($cfg_file, $out);
echo "updated config.local.php\n";
echo "service_account => " . $cfg['google_service_account'] . "\n";
echo "sheet_id => " . $cfg['google_sheet_id'] . "\n";
