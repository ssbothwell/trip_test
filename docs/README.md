# Tripp Backend Test Assignment

### ASSIGMENT

Create a REST based API to add and get user information from a database. You may choose
to use a ACID compliant database, or a NoSQL database.

The application must be written to work with Member objects, whose structure is as follows:

Member

MemberId (int(20), primarykey)
Name (varchar(255), unique)
Email (varchar(255))
Phone (varchar(255))

There should be a REST endpoint for GET, DELETE, and PUT. The REST endpoints must
require authentication via JWT. Assume that the JWKS endpoint is provided for you (or you can
embed the key within the app for this particular task). The JWT issuer is outside the scope of
this test (use a manually created JWT token for testing). The JWT structure should be set up
such that some users only have GET access, some have GET and PUT, and admin users have
access to all endpoints.

The application must leverage a distributed caching server (such as Memcached) to increase
performance.

The application should be written in Java, Python, or C#, and designed to run in a an server
such as Tomcat, but it is NOT necessary to create the deployment packaging (e.g. war file).

If you wish, the application can leverage MVC or ORM libraries like Spring framework, using
class structures/layer separations as appropriate.

There must be unit tests to support and verify functionality of this feature. All business logic
described above should be your original work.

All source code involved must compile successfully. Any library or supporting class files needed
for compilation should be included in the email submission. However, submission with
installation script to demonstrate successful function of the code is optional.


### Implementation Details

### Deployment

### Tests

### Known Issues
