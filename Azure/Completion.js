const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
const endpoint = process.env["AZURE_OPENAI_ENDPOINT"] ;
const azureApiKey = process.env["AZURE_OPENAI_API_KEY"] ;

const messages = [
  { role: "system", content: "You are a helpful chatgpt." },
  { role: "user", content: "I need help with a conditional statement." },
  { role: "assistant", content: "Sure, what conditional statement are you working with?" },
  { role: "user", content: "I have a condition: (a > 10) & (b < 9). Can you provide an integers values for a and b?" },
];


async function main() {
  console.log("== RESPUESTAS DEL CHAT==");

  const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
  const deploymentId = "generacion-de-casos";
  const result = await client.getChatCompletions(deploymentId, messages);

  for (const choice of result.choices) {
    console.log(choice.message);
  }
}

main().catch((err) => {
  console.error("The sample encountered an error:", err);
});

module.exports = { main };