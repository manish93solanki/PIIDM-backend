output=$(curl --location --request POST 'http://localhost:3002/api/user/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "admin@test.com",
    "password": "admin123"
}')
echo "$output"