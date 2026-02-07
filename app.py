import streamlit as st
import time
from chem_logic import MoleculeParser

st.set_page_config(page_title="ChemData Extractor", page_icon="🧪")

st.title("Data Extractor") 
st.sidebar.title("Welcome to the Lab..")


with st.container():
    st.success("Names and CIDs can be used as input")
    st.warning("Beta Version can only process upto 50 compounds per file")

uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:

    file_extension = uploaded_file.name.split('.')[-1].lower()
    allowed_formats = ['txt', 'tsv', 'csv']

    if file_extension not in allowed_formats:
        st.error("Unsupported File Format, Please upload {allowed_formats} files!")
        st.stop()


    raw_content = uploaded_file.getvalue().decode('utf-8')
    parser = MoleculeParser(raw_content)


    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def progress_update(percent):
        progress_bar.progress(percent)

        status_text.write(f"{100 * round(percent,2)}% Reaction Done")

    start = time.perf_counter()


    with st.spinner("Stirring the Solution"):
        parser.run(progress_callback=progress_update)
    
    end = time.perf_counter()
    total_time = round( (end - start), 2)
    col1, col2 = st.columns(2)
    with col1:
        st.success("Compounds Cooked!!!!!")
    with col2:
        st.success(f"The Reaction took {total_time} Seconds")
    df = parser.data_frame_gen()
    if not df.empty:
        st.subheader("Extracted Dataframe")
        st.dataframe(df)

        csv = df.to_csv(sep='\t', index=False).encode('utf-8')
        st.download_button(
            label="Download data as TSV",
            data=csv,
            file_name='molecule_data.tsv',
            mime='text/csv',
        )
    else:
        st.error("We could Not find any valid entry in your file")

    if parser.failed_inputs:    
        st.warning(f"{len(parser.failed_inputs)} compounds failed, Kindly check the names or CIDs again")

        with st.expander("⚠️ View Failed Inputs"):
            for fail in parser.failed_inputs:
                st.write(f"- {fail}")


