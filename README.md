# Spocs Proxy Server
This service sits between Firefox and [AdZerk](https://adzerk.com/).
Its purpose is to preserve the privacy of Firefox clients when they request sponsored content (spocs) for the Firefox New Tab.
See [Sponsored Stories FAQ](https://help.getpocket.com/article/1142-firefox-new-tab-recommendations#sponsoredstories)
for more information.

## API

See [OpenAPI documentation](https://app.swaggerhub.com/apis-docs/PocketNewTab/PocketProxyServer).

## Development environment
The following steps create a Docker development environment to run this service locally.

1. Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
2. In the project root run: `docker-compose build`.
3. Start a mock s3 service: `docker-compose up s3`.
4. Copy [MaxMind GeoIP2](https://dev.maxmind.com/geoip/geoip2/geolite2/) to `pocket-geoip/GeoIP2-City.mmdb` on the mock s3 container.
    1. If the database is stored on s3:
        ```
        images/s3/download.sh -p <aws profile> -b <s3 bucket>
        ```
    2. If it's stored on disk in a file called `GeoLite2-City.mmdb`:
        ```
        aws --endpoint-url http://localhost:4569 s3 cp GeoLite2-City.mmdb s3://pocket-geoip/GeoIP2-City.mmdb
        ```
4. Verify that GeoIP2 is available at [localhost:4569/pocket-geoip/GeoIP2-City.mmdb](http://localhost:4569/pocket-geoip/GeoIP2-City.mmdb).
5. Start the application containers: `docker-compose up`.
6. Test that the application is running: http://localhost/pulse. It should return `{"pulse":"ok"}`.

## Tests
See the [Test README](tests/README.md).

## Deployment

The first time the service is deployed, follow the steps in the [CloudFormation README](cloudformation/README.md).

### Deploy EMR images
Run `./deploy.sh` with the following arguments:
- `-p` AWS profile name from `~/.aws/config`
- `-a` ECR URI for the app container
- `-n` ECR URI for the nginx container

For example:
```bash
./deploy.sh -p pocket-proxy-rw \
-a "12345.dkr.ecr.us-east-1.amazonaws.com/proxy-server-dev:latest" \
-n "12345.dkr.ecr.us-east-1.amazonaws.com/proxy-server-nginx-dev:latest"
```

### Deploy Fargate
Open Fargate in the AWS console and update the service, forcing a new deployment.

# Telemetry Function
The [Telemtry Handler](telemetry/handler.py) is triggered by telemetry from the Firefox discovery stream. It anonymously pings AdZerk to keep track of events related to sponsored content, such as clicks and impressions in a privacy-preserving way. The event code (or "shim") does not contain any personally identifiable data; we never share personal data with AdZerk.

## Deployment
 
1. Open telemetry-proxy in the [Google Cloud Console](https://console.cloud.google.com) 
2. Click Edit and paste the new code
3. Click Deploy
