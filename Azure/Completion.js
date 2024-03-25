const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
require('dotenv').config(); // Cargar variables de entorno desde el archivo .env
const endpoint = process.env["AZURE_OPENAI_ENDPOINT"] ;
const azureApiKey = process.env["AZURE_OPENAI_API_KEY"] ;

const messages = [
  { role: "system", content: "You are a helpful chatgpt." },
  { role: "user", content: "I need help with a conditional statement." },
  { role: "assistant", content: "Sure, what conditional statement are you working with?" },
  { role: "user", content: "Genérame un conjunto de casos de prueba que satisfagan el criterio de cobertura MC/DC para la siguiente expresión booleana." },
  { role: "assistant", content: "Sure, what boolean expresion are you working with?" },
  { role: "user", content: "Con la siguiente expresión booleana:(a>10)&(b<9) ." }, //<inserte aquí la expresión>
  {role:"user",content: "Representa la solución como una lista en Python, donde cada caso de prueba sea un diccionario con el formato {variable: valor}."},
  {role:"user",content: "Respondeme únicamente con la lista de Python, sin explicaciones ni texto extra."}
];



async function main() {
  console.log("== RESPUESTA DEL CHAT==");

  const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
  const deploymentId = "generacion-de-casos";
  const result = await client.getChatCompletions(deploymentId, messages);

  for (const choice of result.choices) {
    console.log(choice.message.content);
  }
}

main().catch((err) => {
  console.error("The sample encountered an error:", err);
});

module.exports = { main };