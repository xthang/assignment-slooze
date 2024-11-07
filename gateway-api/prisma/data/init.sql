INSERT INTO "Account" ("id", "username", "firstName", "lastName", "password", "createdSource", "createdBy")
VALUES ('acc_1', 'account_test', 'TEST', 'TESTT', 'abcd1234', 'sql', 'sql');

INSERT INTO "AccountAlias" ("id", "accountId", "type", "rawValue", "contactValue", "createdBy")
VALUES ('aa_1', 'acc_1', 'emailAddr', 'sa@test.com', 'sa@test.com', 'sql');

INSERT INTO "Organization" (id, "name", "slug", "createdBy")
VALUES ('org_1', 'India', 'india', 'sql');

INSERT INTO "OrganizationMembership" (id, "orgId", "accountId", "role", "createdBy")
VALUES ('mem_1', 'org_1', 'acc_1', 'super_admin', 'sql');

INSERT INTO "MemberRoleAccessMatrix" ("endpoint", "role")
VALUES ('/invite-user', 'super_admin'),

('/order-create', 'super_admin'),
('/order-create', 'admin'),
('/order-create', 'manager'),
('/order-create', 'member'),

('/order-tracking', 'super_admin'),
('/order-tracking', 'admin'),
('/order-tracking', 'manager'),
('/order-tracking', 'member'),

('/payment-create', 'super_admin'),
('/payment-create', 'admin'),
('/payment-create', 'manager'),
('/payment-create', 'member'),

('/pay', 'super_admin'),
('/pay', 'admin'),
('/pay', 'manager'),
('/pay', 'member')
;
