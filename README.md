[![Build Status](https://travis-ci.org/QuantumBA/pyverless.svg?branch=master)](https://travis-ci.org/QuantumBA/pyverless)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyverless.svg)](https://pypi.python.org/pypi/pyverless/)
[![PyPI license](https://img.shields.io/pypi/l/pyverless.svg)](https://pypi.python.org/pypi/pyverless/)
[![PyPI status](https://img.shields.io/pypi/status/pyverless.svg)](https://pypi.python.org/pypi/pyverless/)
# Pyverless

Developing complex APIs within AWS lambdas can be somewhat of a messy task. Lambdas are independent functions that have to work together in order to create a full-blown app, like atoms to a complex organism.

In order to define the infrastructure you may use a framework like [Serverless](https://serverless.com/), but you may find yourself copying and pasting blobs of code within your handler functions, namely for authentication, data validation, error handling and response creation to name a few.

**Enter Pyverless**

Pyverless is a mini-framework with a bunch of utilities that aims to help you create APIs using AWS Lambdas fast and in a consistent way. Pyverless provides the following.

- Class-Based Handlers
- Serializers
- Authentication handling
- JWT and cryptography
- Exceptions
- Configuration
- Warmup handling

Bring more consistency and development speed to your lambda-based APIs!

## Class-Based Handlers

Class based handlers (CBH) use the approach of Django's Class-Based Views to provide code reuse, consistency and generally abstract simple and common tasks. The aim of class-based handlers is to suit a wide range of applications by providing generic Handler classes and mixins.

Within AWS Lambda, a handler is a function that takes an event and a context and returns a response.

Generic CBH are based off the following base handler

### BaseHandler

This class provides the `as_handler()` method that returns a handler function (taking `event` and `context` as arguments).

Usage:

```python
class MyHandler(BaseHandler):
    pass

_myHandler = MyHandler.as_handler()
```

There is a set of generic CBHs to handle basic CRUD operations within an API:

### CreateHandler
Handler that reads the request body and creates the object with each (key, value) pair as a parameter for the constructor.

The `model` attribute must be set on the handler and the `create_object` method can be overwritten.

Usage:

```python
class UserCreateHandler(CreateHandler):

    model = MyUserClass # MyUserClass(k1=v1, k2=v2, ...) for each k,v on body
    required_body_keys = ['email', 'password']
```

### RetrieveHandler
Handler that returns a serialized Object.

The `model` attribute must be set and `id` must be present on the pathParameters.

The user must overwrite either the `serializer` attribute or the `serialize` method.

Usage:

```python
class UserRetrieveHandler(RetrieveHandler):

    model = MyUserClass
    serializer = serialize_user
```

### UpdateHandler
Handler that sets self.object and for each (key, value) pair of the body
sets self.object.key = value.

The `model` attribute must be set and `id` must be present on the pathParameters.

Returns the serialized node and sets the HTTP status code to 200

Usage:

```python
class UserUpdateHandler(UpdateHandler):
    model = MyUserClass
    required_body_keys = ['title', 'body']
    serializer = serialize_user
```


### DeleteHandler
Handler that sets self.object, calls its delete() method and sets the HTTP status code to 204.

The `model` attribute must be set and `id` must be present on the pathParameters.

The user can also overwrite the `get_queryset` method to limit the search.

Usage:

```python
class UserDeleteHandler(DeleteHandler):
    model = MyUserClass
```
### ListHandler
Handler that returns a list of serialized nodes and sets the HTTP status code to 200.

The `model` attribute must be set and the user must overwrite either the `serializer` attribute
or the `serialize` method.

```python
class UserListHandler(ListHandler):
    model = MyUserClass
    serializer = user_serializer
    
    def get_queryset(self):
        return only_some_users
```

## Mixins
There are also a set of **mixins** available:

### RequestBodyMixin

This mixin provides the `get_body()` method which is in charge of gathering the request body dictionary. Define `required_body_keys` and `optinal_body_keys` as follows. Within the handler, you can access the body via `self.body` or by calling `get_body()`

```python
class MyHandler(RequestBodyHandler, BaseHandler):
    required_body_keys = ['name', 'email']
    optinal_body_keys = ['phone']

_myHandler = MyHandler.as_handler()
```

### AuthorizationMixin

This mixin provides the `get_user()` method in charge of getting the user out of an authenticated API call. Within the handler, you can access the body via `self.body` or by calling `get_user()`

### ObjectMixin

This mixin provides the `get_object()` method in charge of gathering a particular object.

### ListMixin

**TODO**


## Serializers

**TODO**