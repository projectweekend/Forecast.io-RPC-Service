This project connects to a [RabbitMQ](http://www.rabbitmq.com/) server and listens for messages. When a message is received on the appropriate queue, weatehr forecast data is gathered from [Forecast.io](https://developer.forecast.io/) and returned to the client that sent the message.


### Installation with Fabric

Using [Fabric](http://www.fabfile.org/) there is an installation task included in this project's `fabfile`:

```
fab local install
```

The task will prompt you for these values:

* `Hostname:` - The hostname of a local computer, for example: `test-server`. Given the example, the Fabric script will attempt to ssh into `test-server.local`.
* `User:` - The user for the local computer so Fabric can connect via SSH.
* `Loggly token:` - The token from your [Loggly](https://www.loggly.com/) account. The service logs data using Loggly which makes it easier to remotely monitor.
* `Loggly domain:` - The domain from your Loggly account.
* `Forecast.io key:` - The API key for [Forecast.io](https://developer.forecast.io/).
* `Rabbit URL:` - The connection URL for the RabbitMQ server. If you don't feel like running your own, check out [CloudAMPQ](https://www.cloudamqp.com/).

The install process will add an [Upstart](http://upstart.ubuntu.com/) script.

To manually stop it:
```
sudo service forecast-rpc stop
```

To manually start it:
```
sudo service forecast-rpc start
```


### Usage

Any script or program can request data from this service provided:

* It has the same `Rabbit URL` value used during installation and can connect to the RabbitMQ server.
* It sends messages to the correct queue (`forecast.get` in this project).


#### JavaScript Example

There are plenty of JavaScript client libraries for RabbitMQ. This example uses [Jackrabbit](https://github.com/hunterloftis/jackrabbit).

```javascript
var jackrabbit = require( "jackrabbit" );

// Use an environment variable for RABBIT_URL
var broker = jackrabbit( process.env.RABBIT_URL, 1 );

var ready = function () {
    // See Forecast.io API documentation for more info about 'options'
    var message = {
        latitude: 41.885246,
        longitude: -87.642853,
        options: {
            exclude: [ "minutely", "daily", "alerts" ]
        }
    };

    // Send a message to request the weather data
    broker.publish( "forecast.get", message, function ( err, data ) {
        if ( err ) {
            // Do something with the error
            console.log( err );
        }
        // Do something with the weather data
        console.log( data );
        process.exit();
    } );
};

var create = function () {
    broker.create( "forecast.get", { prefetch: 5 }, ready );
};

broker.once( "connected", create );
```
