# Access Verify and Client Data Manager

This project consists of two main components: `access_verifier` and `client_data_manager`. These components work together to verify access based on IP addresses and manage client data.

## Access Verifier

The `access_verifier` component is a Flask application that verifies access based on IP addresses. It fetches IP ranges from AWS and allows access based on these ranges and a local IP range.

### Configuration

The configuration for `access_verifier` is stored in [access_verifier/access-verifier-config.yml](access_verifier/access-verifier-config.yml). The main configuration parameters are:

- `AWS_IP_RANGES_URL`: URL to fetch the IP ranges from AWS.
- `LOCAL_IP_RANGE`: Local IP range to allow access.
- `TARGET_REGION`: AWS region to filter IP ranges.
- `FLASK_HOST`: Host for the Flask application.
- `FLASK_PORT`: Port for the Flask application.

### Running the Application

To run the `access_verifier` application, use the following Docker command:

```sh
docker run --rm --name access-verifier -p 8080:8080 access-verifier:0.1
```
### Endpoints

- `/verify`: Handles incoming POST client requests and forwards it to the access_verifier service.


## Client Data Manager

The client_data_manager component is a Flask application that manages client data and verifies access using the access_verifier service.

### Configuration

The configuration for client_data_manager is stored in config.json. The main configuration parameters are:

- `ACCESS_VERIFIER_URL`: URL of the access_verifier service.
- `FLASK_HOST`: Host for the Flask application.
- `FLASK_PORT`: Port for the Flask application.

### Running the Application
To run the client_data_manager application, use the following Docker command:

```sh
docker run --rm --name client-data-manager -p 8081:8081 client-data-manager:0.1
```

### Endpoints

- `/`: Handles incoming client requests and verifies access using the access_verifier service.

## Kubernetes Deployment

Both components can be deployed using Kubernetes. The deployment and service configurations are provided in the respective directories.

### Access Verifier

- `Deployment`: access-verifier-deployment.yaml
- `Service`: access-verifier-service.yaml
- `Config-map`: access-verifier-config.yaml

### Client Data Manager

- `Deployment`: client_data_manager-deployment.yaml
- `Service`: client_data_manager-service.yaml
- `Ingress`: client_data_manager-ingress.yaml

## Building Docker Images

To build the Docker images for both components, use the following commands:

```sh
docker build -t access-verifier:0.1 -f access_verifier/dockerfile access_verifier/
docker build -t client-data-manager:0.1 -f client_data_manager/dockerfile client_data_manager/
```

## Pushing Docker Images

To push the Docker images to a registry, use the following commands:

```sh
docker tag access-verifier:0.1 acrobaticice/access_verifier:0.1
docker tag client-data-manager:0.1 acrobaticice/client_data_manager:0.1

docker push acrobaticice/access_verifier:0.1
docker push acrobaticice/client_data_manager:0.1
```

## Pulling Prebuilt Docker Images

You can pull prebuilt Docker images for both components from the registry using the following commands:

```sh
# Docker image of access_verifier
docker pull acrobaticice/access_verifier:0.1

# Docker image of client_data_manager
docker pull acrobaticice/client_data_manager:0.1
```

These images are ready to use and can be deployed directly without building them locally.

## Testing

To test the access_verifier and client_data_manager services, use the following curl commands:

```sh
# Testing access_verifier
curl -X POST http://localhost:8080/verify -H "Content-Type: text/plain" --data $'Host: localhost:5000\nUser-Agent: curl/7.68.0\nAccept: */*\nX-Forwarded-For: 52.144.218.64/26'

# Testing client_data_manager
curl -X POST http://localhost:8081/ -d "Test payload"
```
