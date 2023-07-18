# Semantic Kernel

## Introduction

In this lab, we're going to build on what we've seen in the previous two labs and introduce Semantic Kernel. Similar to the OpenAI Library, Semantic Kernel provides a layer on top of the OpenAI API, but it also provides an orchestration layer that allows combining different AI models, plugins to bring in information from other sources and concepts like *memories*.

We'll learn about Semantic Kernel by creating a "Hello, World!" application using Azure Functions. We'll use this application to explore the basics of Semantic Kernel, see how an application is structured and then build on that knowledge in later labs.

### Preparation

You can use either GitHub Codespaces (:exclamation:recommended:exclamation:) or you can work locally using Visual Studio Code for this lab.

#### Codespaces Setup

Using Codespaces is the fastest way to get up and running and ready to work with this lab.

In this **Intro to Intelligent Apps** repo in GitHub, click the green "<> Code" button, then choose "Codespaces" and click the button "Create codespace on main".

A new Codespace will be setup. The build process takes around 10 to 15 minutes to complete.

#### Visual Studio Code Setup

If you want to work locally using Visual Studio Code on your own device, we recommend using the *DevContainer* that's part of this repo. The DevContainer is prepared with all of the components needed to complete this lab.

You'll need **Docker Desktop**, **Visual Studio Code** and the **Remote - Containers** extension installed to use a DevContainer

* Install [Docker](https://www.docker.com/products/docker-desktop)
* Install [Visual Studio Code](https://code.visualstudio.com/)
* Install [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

With those installed, follow these steps to prepare and start the DevContainer

* Clone this repository
* Open the repository in Visual Studio Code
* Click on the green button in the bottom left corner of the window
* Select `Reopen in Container`
* Wait for the container to be built and started

#### Start from Scratch

If you really want to, you can start from scratch, but there will be a few components you'll need to find and install! To start from scratch, you can either use a clean, new repo with Codespaces in GitHub, or you can work locally.

The pre-requisites for a "from scratch" setup are

- GitHub Codespaces or Visual Studio Code
- Dotnet 6
- Visual Studio Code extension for Semantic Kern

---

## Let's go!

You should have a working environment with Codespaces or Visual Studio Code ready to go now. So, let's go ahead and create our first Semantic Kernel application.

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
