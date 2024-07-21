from crewai_tools import ScrapeWebsiteTool


import os
os.environ["OPENAI_API_KEY"] = ''

# To enable scrapping any website it finds during it's execution

tool = ScrapeWebsiteTool()
print("test branchhhhhhhhhhhhhhhhhhhh")

print("new changess fileee testbranch")



print("test branch 222222222222222222222222222222")




print("changes test branch333333333")

# Initialize the tool with the website URL, so the agent can only scrap the content of the specified website

tool = ScrapeWebsiteTool(website_url='https://docs.crewai.com/core-concepts/Agents/')



# Extract the text from the site

text = tool.ru()

print(text)




from crewai_tools import WebsiteSearchTool

import os
os.environ["OPENAI_API_KEY"] = ''
print(333333333333333333333333333333333333333333333333)

# Example of initiating tool that agents can use to search across any discovered websites

tool = WebsiteSearchTool()



# Example of limiting the search to the content of a specific website, so now agents can only search within that website

website_result = WebsiteSearchTool(website='https://docs.crewai.com/tools/WebsiteSearchTool/#installation')

result = website_res.text()
print(result)