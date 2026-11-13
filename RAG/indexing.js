import path from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import {PDFLoader} from '@langchain/community/document_loaders/fs/pdf'
import {OpenAIEmbeddings} from '@langchain/openai'
import {QdrantVectorStore} from '@langchain/qdrant'

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const generateEmbeddingsForFile= async (filepath)=>{

    //laod the  pdf content as documents
    const loader = new PDFLoader(filepath)
    const docs= await loader.load() //already chunks data page  by page 

    //initialize the embeddings model

    const embeddings = new OpenAIEmbeddings({
        model: 'text-embedding-3-small',
        apiKey: process.env.OPENAI_API_KEY
    })

    //initialize the vector store
    const vectorStore = await QdrantVectorStore.fromExistingCollection(
        embeddings, //  use this  emmbedding model
        {
            url: "http://localhost:6333",
            collectionName: 'pdf-collection'
        }
       
    )
    await vectorStore.addDocuments(docs)
    console.log('Documents indexed successfully')


}
generateEmbeddingsForFile(path.join(__dirname, "DSA.pdf"))