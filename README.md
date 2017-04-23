# ml_deploy
An api to both organize and deploy machine learning models in your organization.

ml_deploy will both store your python ml models and it's various attributes, allowing it to be called from anywhere.
It includes an easy interface to set up both predictions from batches and eventually streamed results.

Creating a user is as easy the following:
```shell
curl --request POST \
  --url 'http://localhost:8006/account?username=coolUser&password=testPassword'
```
