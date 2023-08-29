# Prompts Demos

In this document you will find demos for the "Intro to Azure OpenAI, Prompt Engineering & Demos" morning session. The demos are aimed at showing how certain prompts can be made better by following recommended prompt engineering practices.

**All of these demos can be done using Azure AI Studio.**

## :muscle: Demo 1 - Separate instruction and context

* Good:

```text
Summarize the text below as a bullet point list of the most important points.

We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.

In pursuit of our mission to ensure advanced AI benefits all of humanity, OpenAI remains a capped-profit company and is governed by the OpenAI non-profit. This structure allows us to raise the capital we need to fulfill our mission without sacrificing our core beliefs about broadly sharing benefits and the need to prioritize safety. Microsoft shares this vision and our values, and our partnership is instrumental to our progress.
```

* Better:

```text
Summarize the text below as a bullet point list of the most important points.

"""
We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.

In pursuit of our mission to ensure advanced AI benefits all of humanity, OpenAI remains a capped-profit company and is governed by the OpenAI non-profit. This structure allows us to raise the capital we need to fulfill our mission without sacrificing our core beliefs about broadly sharing benefits and the need to prioritize safety. Microsoft shares this vision and our values, and our partnership is instrumental to our progress.
"""
```

## :muscle: Demo 2 - Be specific, descriptive and as detailed as possible

* Good:

```text
Write a poem about OpenAI.
```

* Better:

```text
Write a short inspiring poem about OpenAI, focusing on the recent DALL-E product launch in the style of Ernest Hemingway.
```

## :muscle: Demo 3 - Articulate the desired output format through examples

* Good:

```text
Extract the company names then years in the following text below and output start index and end index of each entity. Generate output as {"text": "OpenAI", "start": 28, "end": 34}

###
We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.


###
```

* Better:

```text
Extract the entities mentioned in the text below. Extract the important entities mentioned in the text below. First extract all company names, then extract all years, then extract specific topics which fit the content and finally extract general overarching themes.

Desired format:
Company names: <comma_separated_list_of_company_names>
Years: -||-
Specific topics: -||-
General themes: -||-

"""
We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.


"""
```

## :muscle: Demo 4 - Reduce fluffy and imprecise descriptions

* Good:

```text
Write a description for a new product. This product is a new generation of car seat. The description for this product should be fairly short, a few sentences only, and not too much more.
```

* Better:

```text
Write a description for a new product. This product is a new generation of car seat. Use a 3 to 5 sentence paragraph to describe this product.
```

## :muscle: Demo 5 - Instead of just saying what not to do, say what to do instead

* Good:

```text
The following is a conversation between an Agent and a Customer. DO NOT ASK USERNAME OR PASSWORD. DO NOT REPEAT.

Customer: I can’t log in to my account.
Agent:
```

* Better:

```text
The following is a conversation between an Agent and a Customer. The agent will attempt to diagnose the problem and suggest a solution, whilst refraining from asking any questions related to PII. Instead of asking for PII, such as username or password, refer the user to the help article www.samplewebsite.com/help/faq

Customer: I can’t log in to my account.
Agent:
```

## :muscle: Demo 6 - Start with zero-shot, then few-shot (example), neither of them worked, then fine-tune

* Good:

```text
Extract keywords from the below text. Text:
We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.

Keywords:
```

* Better:

```text
Extract keywords from the corresponding texts below.

Text 1: Stripe provides APIs that web developers can use to integrate payment processing into their websites and mobile applications.
Keywords 1: Stripe, payment processing, APIs, web developers, websites, mobile applications
##
Text 2: OpenAI has trained cutting-edge language models that are very good at understanding and generating text. Our API provides access to these models and can be used to solve virtually any task that involves processing language.
Keywords 2: OpenAI, language models, text processing, API.
##
Text 3: We’re happy to announce that OpenAI and Microsoft are extending our partnership. This multi-year, multi-billion dollar investment from Microsoft follows their previous investments in 2019 and 2021, and will allow us to continue our independent research and develop AI that is increasingly safe, useful, and powerful.
Keywords 3:
```