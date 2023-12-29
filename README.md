# dagster-demo-user-code

## Image Build & Push

```shell
GOOGLE_CLOUD_PROJECT=gke-demo-355900
```

```shell
docker build \
  -t "us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/dagster-demo/dagster-demo-user-code:latest" \
  -f ./Dockerfile .
```

```shell
docker push \
  "us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/dagster-demo/dagster-demo-user-code:latest"
```