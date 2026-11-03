# Run the Bruno API Calls with curl

Use this guide if Bruno is not installed. It runs the same requests as the
collection from a macOS Terminal or Windows PowerShell.

The examples prompt for credentials instead of putting secrets directly in
your shell history. Keep the returned tokens and credentials private. The
tokens are stored only in variables in the current terminal session.

Run all steps for your platform in the same terminal session. Opening another
terminal loses the variables created by earlier steps.

## macOS Terminal

These commands target `zsh`, the default shell on current macOS versions. They
require `curl` and [`jq`](https://jqlang.github.io/jq/) for processing JSON.
Confirm that both are available:

```zsh
curl --version
jq --version
```

If `jq` is missing and you use Homebrew, install it with `brew install jq`.

### 1. Configure the connection

Enter base URLs without a trailing slash.

```zsh
read "IAS_HOST?IAS host (for example, https://tenant.accounts.cloud.sap): "
read "CLIENT_ID?Client ID: "
read -s "CLIENT_SECRET?Client secret: "; echo
read "USERNAME?IAS username: "
read -s "PASSWORD?IAS password: "; echo
read "AGENT_GATEWAY_HOST?Agent Gateway host (for example, https://eu10.access.sapdas.cloud.sap): "

AGENT_GATEWAY_RESOURCE='urn:sap:identity:application:provider:name:agent-gateway'
```

### 2. Fetch the user token

This is equivalent to **(1) Fetch User Token**.

```zsh
IAS_USER_TOKEN="$(
  curl --silent --show-error --fail-with-body \
    --request POST "$IAS_HOST/oauth2/token" \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=password' \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET" \
    --data-urlencode "username=$USERNAME" \
    --data-urlencode "password=$PASSWORD" \
    --data-urlencode 'token_format=jwt' \
  | jq --exit-status --raw-output '.access_token'
)"
```

### 3. Exchange the user token

This is equivalent to **(2) Exchange User Token**.

```zsh
AGENT_GATEWAY_TOKEN="$(
  curl --silent --show-error --fail-with-body \
    --request POST "$IAS_HOST/oauth2/token" \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer' \
    --data-urlencode "assertion=$IAS_USER_TOKEN" \
    --data-urlencode "resource=$AGENT_GATEWAY_RESOURCE" \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET" \
    --data-urlencode 'token_format=jwt' \
  | jq --exit-status --raw-output '.access_token'
)"
```

### 4. Fetch the ARD document

This is equivalent to **(3) Fetch ARD Document**.

```zsh
ARD_DOCUMENT="$(
  curl --silent --show-error --fail-with-body \
    "$AGENT_GATEWAY_HOST/v1/.well-known/ard.json" \
    --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN"
)"

printf '%s\n' "$ARD_DOCUMENT" | jq .
```

List only callable agents and their agent-card URLs:

```zsh
printf '%s\n' "$ARD_DOCUMENT" \
  | jq --raw-output '.entries[] | select(.metadata.callable == true) | [.displayName, .url] | @tsv'
```

Copy the `url` of the agent you want to invoke, then enter it when prompted:

```zsh
read "JOULE_AGENT_AGENT_CARD_URL?Callable agent-card URL: "
```

### 5. Fetch the agent card

This is equivalent to **(4) Fetch Agent Card**. The A2A server URL is read from
the top-level `url` field automatically.

```zsh
AGENT_CARD="$(
  curl --silent --show-error --fail-with-body \
    "$JOULE_AGENT_AGENT_CARD_URL" \
    --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN"
)"

printf '%s\n' "$AGENT_CARD" | jq .
JOULE_AGENT_A2A_SERVER_URL="$(printf '%s\n' "$AGENT_CARD" | jq --exit-status --raw-output '.url')"
printf 'A2A server URL: %s\n' "$JOULE_AGENT_A2A_SERVER_URL"
```

### 6. Invoke the agent

This is equivalent to **(5) Invoke Agent**. The response can take up to two
minutes.

```zsh
read "AGENT_MESSAGE?Message (press Enter for 'What can you do for me?'): "
AGENT_MESSAGE="${AGENT_MESSAGE:-What can you do for me?}"

REQUEST_BODY="$(
  jq --null-input \
    --arg request_id "$(uuidgen)" \
    --arg message_id "$(uuidgen)" \
    --arg text "$AGENT_MESSAGE" \
    '{
      jsonrpc: "2.0",
      id: $request_id,
      method: "message/send",
      params: {
        message: {
          role: "user",
          parts: [{kind: "text", text: $text}],
          messageId: $message_id,
          kind: "message"
        },
        configuration: {blocking: true}
      }
    }'
)"

printf '%s' "$REQUEST_BODY" \
  | curl --silent --show-error --fail-with-body \
      --request POST "$JOULE_AGENT_A2A_SERVER_URL" \
      --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN" \
      --header 'Content-Type: application/json' \
      --data-binary @- \
  | jq .
```

## Windows PowerShell

These commands work in Windows PowerShell 5.1 and PowerShell 7. Use
`curl.exe`, not `curl`, because Windows PowerShell may define `curl` as an
alias for `Invoke-WebRequest`.

Confirm that curl is available before continuing:

```powershell
curl.exe --version
```

### 1. Configure the connection

Enter base URLs without a trailing slash. The helper reads secrets without
displaying them.

```powershell
function Read-PlainTextSecret {
    param([string] $Prompt)

    $secureValue = Read-Host $Prompt -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
    try {
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

$IAS_HOST = Read-Host "IAS host (for example, https://tenant.accounts.cloud.sap)"
$CLIENT_ID = Read-Host "Client ID"
$CLIENT_SECRET = Read-PlainTextSecret "Client secret"
$USERNAME = Read-Host "IAS username"
$PASSWORD = Read-PlainTextSecret "IAS password"
$AGENT_GATEWAY_HOST = Read-Host "Agent Gateway host (for example, https://eu10.access.sapdas.cloud.sap)"
$AGENT_GATEWAY_RESOURCE = "urn:sap:identity:application:provider:name:agent-gateway"
```

### 2. Fetch the user token

This is equivalent to **(1) Fetch User Token**.

```powershell
$response = curl.exe --silent --show-error --fail-with-body `
    --request POST "$IAS_HOST/oauth2/token" `
    --header "Content-Type: application/x-www-form-urlencoded" `
    --data-urlencode "grant_type=password" `
    --data-urlencode "client_id=$CLIENT_ID" `
    --data-urlencode "client_secret=$CLIENT_SECRET" `
    --data-urlencode "username=$USERNAME" `
    --data-urlencode "password=$PASSWORD" `
    --data-urlencode "token_format=jwt"
if ($LASTEXITCODE -ne 0) { throw "Fetching the user token failed." }
$IAS_USER_TOKEN = (($response -join "`n") | ConvertFrom-Json).access_token
```

### 3. Exchange the user token

This is equivalent to **(2) Exchange User Token**.

```powershell
$response = curl.exe --silent --show-error --fail-with-body `
    --request POST "$IAS_HOST/oauth2/token" `
    --header "Content-Type: application/x-www-form-urlencoded" `
    --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" `
    --data-urlencode "assertion=$IAS_USER_TOKEN" `
    --data-urlencode "resource=$AGENT_GATEWAY_RESOURCE" `
    --data-urlencode "client_id=$CLIENT_ID" `
    --data-urlencode "client_secret=$CLIENT_SECRET" `
    --data-urlencode "token_format=jwt"
if ($LASTEXITCODE -ne 0) { throw "Exchanging the user token failed." }
$AGENT_GATEWAY_TOKEN = (($response -join "`n") | ConvertFrom-Json).access_token
```

### 4. Fetch the ARD document

This is equivalent to **(3) Fetch ARD Document**.

```powershell
$response = curl.exe --silent --show-error --fail-with-body `
    "$AGENT_GATEWAY_HOST/v1/.well-known/ard.json" `
    --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN"
if ($LASTEXITCODE -ne 0) { throw "Fetching the ARD document failed." }
$ARD_DOCUMENT = ($response -join "`n") | ConvertFrom-Json
$ARD_DOCUMENT | ConvertTo-Json -Depth 100
```

List only callable agents and their agent-card URLs:

```powershell
$ARD_DOCUMENT.entries `
    | Where-Object { $_.metadata.callable -eq $true } `
    | Select-Object displayName, url `
    | Format-Table -AutoSize -Wrap
```

Copy the `url` of the agent you want to invoke, then enter it when prompted:

```powershell
$JOULE_AGENT_AGENT_CARD_URL = Read-Host "Callable agent-card URL"
```

### 5. Fetch the agent card

This is equivalent to **(4) Fetch Agent Card**. The A2A server URL is read from
the top-level `url` field automatically.

```powershell
$response = curl.exe --silent --show-error --fail-with-body `
    "$JOULE_AGENT_AGENT_CARD_URL" `
    --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN"
if ($LASTEXITCODE -ne 0) { throw "Fetching the agent card failed." }
$AGENT_CARD = ($response -join "`n") | ConvertFrom-Json
$AGENT_CARD | ConvertTo-Json -Depth 100
$JOULE_AGENT_A2A_SERVER_URL = $AGENT_CARD.url
Write-Host "A2A server URL: $JOULE_AGENT_A2A_SERVER_URL"
```

### 6. Invoke the agent

This is equivalent to **(5) Invoke Agent**. Piping the body to `curl.exe`
avoids JSON quoting differences between Windows PowerShell versions. The
response can take up to two minutes.

```powershell
$AGENT_MESSAGE = Read-Host "Message (press Enter for 'What can you do for me?')"
if ([string]::IsNullOrWhiteSpace($AGENT_MESSAGE)) {
    $AGENT_MESSAGE = "What can you do for me?"
}

$requestObject = @{
    jsonrpc = "2.0"
    id = [guid]::NewGuid().ToString()
    method = "message/send"
    params = @{
        message = @{
            role = "user"
            parts = @(
                @{
                    kind = "text"
                    text = $AGENT_MESSAGE
                }
            )
            messageId = [guid]::NewGuid().ToString()
            kind = "message"
        }
        configuration = @{
            blocking = $true
        }
    }
}
$requestBody = $requestObject | ConvertTo-Json -Depth 10 -Compress

$response = $requestBody | curl.exe --silent --show-error --fail-with-body `
    --request POST "$JOULE_AGENT_A2A_SERVER_URL" `
    --header "Authorization: Bearer $AGENT_GATEWAY_TOKEN" `
    --header "Content-Type: application/json" `
    --data-binary "@-"
if ($LASTEXITCODE -ne 0) { throw "Invoking the agent failed." }
(($response -join "`n") | ConvertFrom-Json) | ConvertTo-Json -Depth 100
```

## Optional: Technical Token Discovery

The collection also contains **(9.1) Fetch Client Credentials (Technical
Token)** and **(9.2) Fetch ARD Document (Technical Token)**. These requests are
not needed for the user-token flow above.

On macOS:

```zsh
TECHNICAL_TOKEN="$(
  curl --silent --show-error --fail-with-body \
    --request POST "$IAS_HOST/oauth2/token" \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=client_credentials' \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET" \
    --data-urlencode 'token_format=jwt' \
    --data-urlencode "resource=$AGENT_GATEWAY_RESOURCE" \
  | jq --exit-status --raw-output '.access_token'
)"

curl --silent --show-error --fail-with-body \
  "$AGENT_GATEWAY_HOST/v1/.well-known/ard.json" \
  --header "Authorization: Bearer $TECHNICAL_TOKEN" \
| jq .
```

On Windows PowerShell:

```powershell
$response = curl.exe --silent --show-error --fail-with-body `
    --request POST "$IAS_HOST/oauth2/token" `
    --header "Content-Type: application/x-www-form-urlencoded" `
    --data-urlencode "grant_type=client_credentials" `
    --data-urlencode "client_id=$CLIENT_ID" `
    --data-urlencode "client_secret=$CLIENT_SECRET" `
    --data-urlencode "token_format=jwt" `
    --data-urlencode "resource=$AGENT_GATEWAY_RESOURCE"
if ($LASTEXITCODE -ne 0) { throw "Fetching the technical token failed." }
$TECHNICAL_TOKEN = (($response -join "`n") | ConvertFrom-Json).access_token

$response = curl.exe --silent --show-error --fail-with-body `
    "$AGENT_GATEWAY_HOST/v1/.well-known/ard.json" `
    --header "Authorization: Bearer $TECHNICAL_TOKEN"
if ($LASTEXITCODE -ne 0) { throw "Fetching the ARD document failed." }
(($response -join "`n") | ConvertFrom-Json) | ConvertTo-Json -Depth 100
```

If an access token expires, repeat the user-token and token-exchange steps
before calling the Agent Gateway again.

## Troubleshooting

- Copy only the URL value, such as `https://tenant.accounts.cloud.sap`. Do not
  include Markdown link characters (`[`, `]`, `(`, or `)`).
- Enter base URLs without a trailing slash and run every block in the same
  terminal session.
- On macOS, `command not found: jq` means `jq` must be installed before running
  the examples.
- On Windows, use `curl.exe`. If `curl.exe --version` fails, install a current
  curl build or use PowerShell 7 on a supported Windows version.
- An HTTP `401` normally indicates an incorrect username, password, client ID,
  or client secret. An HTTP `403` normally indicates a missing formation or
  authorization for the requested Agent Gateway resource.
- A successful run obtains two bearer tokens, finds at least one ARD entry with
  `metadata.callable` set to `true`, loads an agent card whose `url` ends in
  `/jsonrpc`, and receives a JSON-RPC response containing `result` rather than
  `error`.
