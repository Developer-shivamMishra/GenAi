const { OpenAIEmbeddings } = require("langchain/embeddings/openai");
const { QdrantVectorStore } = require("langchain/vectorstores/qdrant");
const {OpenAI}  = require("@langchain/openai")

const model = new OpenAI({
    model: "gpt-4o-mini",
    apiKey: process.env.OPENAI_API_KEY
})
const query = async (userQuery) => {
    //convert user query to vector embedding
    const embeddings = new OpenAIEmbeddings({
        model: 'text-embedding-3-small',
        apiKey: process.env.OPENAI_API_KEY
    })
    //search vector  in the qdrant database
    const vectorStore = await QdrantVectorStore.fromExistingCollection(
        embeddings, //  use this  emmbedding model
        {
            url: "http://localhost:6333",
            collectionName: 'pdf-collection'
        }
       
    )
    
    //get  similar  vecotor and chunks

    const vectorRetriever = await vectorStore.asRetriever({k :5})
    const results = await vectorRetriever.invoke(userQuery)
  
    //feed those chunks to the LLM model and do a simple chat with {userQuery}

    const SYSTEM_PROMPT = `
    You are an expret  AI assistant that can ANSWER user queries based on the provided context.
    do not answer anything  beyond the context provided.

    User docments : 

    ${results.map(result =>JSON.stringify({page_content: result.page_content, page_number: result.metadata.page_number})).join('\n')}


    `

    const llmResponse =  await  client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            {role: "system", content: SYSTEM_PROMPT},
            {role: "user", content: userQuery}
        ]
    })
    return llmResponse.choices[0].message.content
}

query("What is the main topic of the document?")