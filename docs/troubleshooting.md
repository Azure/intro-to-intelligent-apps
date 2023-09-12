# Troubleshooting

This is a list of the most common errors that we saw occuring and their solutions

## Operation Not Supported

This error might occur, when calling a GPT-3 model:

```json
{
  "error": {
    "code": "OperationNotSupported",
    "message": "The completion operation does not work with the specified model, gpt-35-turbo. Please choose different model and try again. You can learn more about which models can be used with each operation here: https://go.microsoft.com/fwlink/?linkid=2197993."
  }
}
```

This usually means, that you are using an unsupported version of the GPT 3.5 model. Please check your deployment and make sure you are using version `0301`. Newer versions might include breaking changes that this workshop has not yet been updated to.

If you Azure Open AI servcie does not offer you to deploy a GPT 3.5 model with version `0301`, please try to deploy an Azure Open AI service to a different Azure Region like West Europe.
