curl --location --request POST 'http://localhost:3002/api/user_role/add' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "name": "super_admin"
    },
    {
        "name": "agent"
    },
    {
        "name": "student"
    }
]'

curl --location --request POST 'http://localhost:3002/api/user/add' \
--header 'Content-Type: application/json' \
--data-raw '
    {
        "name": "admin",
        "phone_num": "+91-0000000000",
        "email": "admin@test.com",
        "password": "admin123",
        "user_role_id": 1
    }
'


output=$(curl --location --request POST 'http://localhost:3002/api/user/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "admin@test.com",
    "password": "admin123"
}')
echo "$output"