import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
# Θα χρησιμοποιήσουμε δωρεάν embeddings από το HuggingFace για να μην χρεωνόμαστε
from langchain_community.embeddings import HuggingFaceEmbeddings 
import os

st.title("Cloud AI Agent με τα έγγραφά σου")

# Σύνδεση με το Groq API (Θα τραβάει το κλειδί από τις ρυθμίσεις του server)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.warning("Παρακαλώ πρόσθεσε το GROQ_API_KEY στις ρυθμίσεις περιβάλλοντος.")
else:
    # Αρχικοποίηση του μοντέλου Llama 3 μέσω Groq
    llm = ChatGroq(groq_api_key=api_key, model_name="llama3-8b-8192")
    
    # Επιλογή αρχείου PDF από τον χρήστη
    uploaded_file = st.file_uploader("Ανέβασε ένα αρχείο PDF", type=["pdf"])
    
    if uploaded_file:
        # Αποθήκευση του αρχείου προσωρινά για να το διαβάσει ο Loader
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
            
        # Διάβασμα και επεξεργασία του PDF
        loader = PyPDFLoader("temp.pdf")
        docs = loader.load()
        
        # Σπάσιμο του κειμένου σε μικρά κομμάτια (Chunks)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Δημιουργία Vector Store στη μνήμη της εφαρμογής
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()
        
        st.success("Το έγγραφο αναλύθηκε επιτυχώς! Μπορείς να κάνεις ερωτήσεις.")
        
        # Περιοχή Chatbox
        user_question = st.text_input("Κάνε μια ερώτηση σχετικά με το έγγραφο:")
        if user_question:
            # Αναζήτηση των σχετικών κομματιών κειμένου
            relevant_docs = retriever.get_relevant_documents(user_question)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Δημιουργία του prompt για το μοντέλο
            prompt = f"Βασίσου στις παρακάτω πληροφορίες για να απαντήσεις στην ερώτηση.\n\nΠληροφορίες:\n{context}\n\nΕρώτηση: {user_question}"
            
            # Λήψη απάντησης
            response = llm.invoke(prompt)
            st.write("### Απάντηση:")
            st.write(response.content)
            