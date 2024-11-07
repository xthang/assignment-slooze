Slooze projects

NOTE:

- The final system might/should be designed as micro-services. The app in '/gateway-api' will act as access-control gateway API.
- After starting the app, you can view the API collection at: http://localhost:8000/docs

HOW TO START:

1. Install Python 3.
2. Install Make (you can skip this if you know how to run script directly from Makefile).
3. Install Docker. Then run 'docker-compose.yml' to install local Posgresql.
   You can skip this step if you already have another Postgres DB installed.
4. Create a new DB instance. Get its connection URL.
5. (optional) Create Python Virtual Environment and activate it.
   Read: https://docs.python.org/3/library/venv.html
6. Install project's dependencies: `pip install -r requirements.txt`.
7. This project use Prisma as ORM. We need to push Prisma schema to the DB schema: `dotenv -e .env.development prisma db push` OR `make prisma-push`.
8. Generate Prisma files: `prisma generate` OR `make prisma-generate`.
9. Generate initial data by running SQL script: '/prisma/data/init.sql' to insert base data: Super user, organization, etc.
10. Run `python main.py` to start the app

DEMO:

1. Super Admin sign-in:
   `curl --location 'http://127.0.0.1:8000/sign-in' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'email=sa@test.com' \
--data-urlencode 'password=abcd1234'`
2. Super Admin sends a invitation to invite 'admin@test.com' to the organization:
   `curl --location 'http://127.0.0.1:8000/invite-user' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--header 'Authorization: ••••••' \
--data-urlencode 'email=admin@test.com' \
--data-urlencode 'role=admin'`
   This will insert a record into DB table 'TaskSendEmail'. You can find the content of the email there.
3. The invited user accepts the invitation by clicking the URL, which will open the Sign-up page.
   After the user inputs all required data, the page send a request to Backend API to sign the user up:
   `curl --location 'http://127.0.0.1:8000/sign-up-by-invitation' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im5neHRAeWFob28uY29tIiwib3JnLWlkIjoib3JnXzEiLCJyb2xlIjoiYWRtaW4iLCJpbnZpdGVkLWJ5IjoiYWNjXzEifQ.CKURtiSLsOBz7kesSQ8Dtk3udg_Uj3LeBldQbwleKgdsAdhsENDvi0RqNu7MH5dnBRoejD3t4-xlvpfmlJA_eb6KnBW5M7YyunuIDLInS2dgehikryjX-NuEUoInyewVXG0vgFdGj9FGNLOjlbOKJV7tBXCO92vgr5RK7l6PNylVKA-gJ7Df8v-Nu9ZT56mVq3AU5VSa30LaaNShICdXeZ1djTGT1cEDmschdxxDrkjPNHOe047O8Ka4F8B-6QsgVjZMLWBsj_oLjnEEQeY-XYekkrGAJBtVh9X8NcyiwHV_mVCGRVtMXW7p6jWIpOaHmHvePiVftj1Oh0OPFhsogA' \
--data-urlencode 'username=admin' \
--data-urlencode 'first_name=Firsttt' \
--data-urlencode 'last_name=Lasttt' \
--data-urlencode 'password=abcd1234'`
4. The admin user now can sign-in and send request to the backend API to make permitted requests.
