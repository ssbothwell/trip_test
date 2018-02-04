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

I wrote this REST server using Flask, SQLite3 database, and 
the Flask-JWT-Exended plugin. The database contains a the

`members` table as described in the assignment and a `users`
table for access control and JWT token generation. Users must
hit `/login` route with a `POST` request containing valid 
username and password from the `users` table. Passwords are
not hashed because there is no frontend and no registration
system. It is assumed that hashing would happen at those points.

`/login` returns a JSON response with a JWT access token. The
token can then be attached as a header to requests to REST api
for authentication. Users have a hierarchical access control
assigned in the database: 
        
        `access_rights` == 0 = no access (blacklisted user)
        `access_rights` => 1 = GET requests
        `access_rights` => 2 = PUT requests
        `access_rights` == 3 = DELETE requests



### Deployment

```
$ gunicorn application:app
```

### Tests

```
$ py.test tests/
```

### Known Issues

SQLite database is not suitable for cloud server setups such
as Heroku. I plan to switch to PostgreSQL

I also am not sure how well Memcached will integrate with SQLite.
I am currently looking into this.

Production specific environment variables are not currently 
defined yet. I think the implementation of this will be affected
by my choice of cloud service provider.
