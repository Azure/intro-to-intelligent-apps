# Semantic Kernel with Azure Functions

## Introduction

In this lab, we're going to build on what we've seen in the previous labs around Semantic Kernel and see how that can be used with Azure Functions.

We'll learn by creating a "Hello, World!" application using Azure Functions. We'll use this application to explore the basics of Semantic Kernel, see how an application is structured and then build on that knowledge in later labs.

## Let's go!

You should have a working environment with Codespaces or Visual Studio Code ready to go now. So, let's go ahead and create our first Semantic Kernel application.

### Install .NET 6.0 Runtime

This codespace does not include the .NET 6.0 runtime which is required for the Semantic Kernel extension to function correctly. Follow the instructions below to install the runtime.

1. wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
2. chmod +x dotnet-install.sh
3. sudo ./dotnet-install.sh --channel 6.0 --install-dir /usr/share/dotnet

### Create the Azure Function application

- Open the Visual Studio Code command palette and look for `Semantic Kernel: Create Project'
- Choose the **C# Azure Functions** option
- Choose a location for the application to be created in. A new folder will be automatically created at this location.

### Explore the application

Before we start the application, let's take at what's been created.

Examine the `config` folder. Here you will find various files used to setup the application to work with the Azure Open AI or Open AI services. This includes an `appconfig.json` file which we'll need to configure appropriately later.

Examine the `skills` folder. Here you will find plug-ins that are used to interact with Open AI services in different ways.

Explore the contents of the `Excuses` folder which you'll find under `skills/FunSkill`. What do you see?

### Test the Azure Function application

Before we can successfully start the Functions application, we need to provide some configuration details. 

Go to the `config` folder we explored earlier and create the appropriate configuration to point to the Azure OpenAI Service that you're using. When the application was created, a `README.md` file was created which will help you understand what values you need to provide.

Once you've setup the configuration correctly, follow the instructions in the `README.md` file to build and run the Azure Function application.

When the Function Application starts, the console will display the URL that can be used to access the application. Make a note of this URL as you will need it later.

<details>
  <summary>:white_check_mark: Sample URL</summary>

  http://localhost:7071/api/skills/{skillName}/functions/{functionName}
  
</details>

You can now invoke the "Excuses" function under the "FunSkill" skill using a tool like `curl` or Postman. 

<details>
  <summary>:white_check_mark: Example payload and `curl` command</summary>

  [Sample payload](payload-excuses.json)

  **payload-excuses.json**
  ```json
  {
    "variables": [
        {
            "key": "input",
            "value": "Homework."
        }
    ]
  }
  ```

  Sample `curl` command

  ```
  curl -X POST "http://localhost:7071/api/skills/FunSkill/functions/Excuses/" -d @payload-excuses.json
  ```
  
</details>

## Add Custom Semantic Skill

Now that you have seen it in action, let's add a custom semantic skill. Use one of the prompts from the earlier exercise or feel free to use your own. The prompt should have at least one variable, {{$input}}, to help demonstrate how to make a prompt dynamic versus just being static.

1. Add a new skill directory along with function directory in the "skills" folder.
2. Add "config.json" and "skprompt.txt" files to the function directory, be sure to use your own **prompt** and configuration.
3. Restart your function so the new skill will be loaded.
4. Invoke the "YOUR_NEWLY_CREATED_FUNCTION" function under the "YOUR_NEW_SKILL" skill using curl or postman.

Assuming all the above executes correctly, you have now turned your OpenAI prompt into a rest-based API that can be leveraged across the Enterprise. Yay!
