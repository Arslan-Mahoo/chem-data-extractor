import streamlit as st
import time
from chem_logic import MoleculeParser

# Title and Header Data (Must be the first Streamlit command)
st.set_page_config(page_title="ChemData Extractor", page_icon="🧪")

name_col, tagline_col = st.columns(2)
with name_col:
    st.title("⚗️Chemly") 
with tagline_col:
    st.title("Pubchem Scraper")
st.sidebar.title("Welcome to the Lab..")

# --- State Management Initialization ---
# We use these keys to remember data across reruns
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

if "molecule_obj" not in st.session_state:
    st.session_state.molecule_obj = None

if "reaction_time" not in st.session_state:
    st.session_state.reaction_time = 0

with st.container():
    st.success("Names and CIDs can be used as input")
    st.warning("Beta Version can only process upto 50 compounds per file")

uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv', 'tsv'])

if uploaded_file is not None:
    # File validation logic
    file_extension = uploaded_file.name.split('.')[-1].lower()
    allowed_formats = ['txt', 'tsv', 'csv']

    if file_extension not in allowed_formats:
        st.error(f"Unsupported File Format, Please upload {allowed_formats} files!")
        st.stop()

    # --- LOGIC BRANCH 1: Data Processing ---
    # Only show the "Start" button if we haven't processed data yet
    if st.session_state.processed_df is None:
        
        if st.button("⚗️ Start Reaction"):
            raw_content = uploaded_file.getvalue().decode('utf-8')
            parser = MoleculeParser(raw_content) #
            
            # UI Elements for progress
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def progress_update(percent):
                progress_bar.progress(percent)
                status_text.write(f"{100 * round(percent,2)}% Reaction Done")

            start = time.perf_counter()

            with st.spinner("Stirring the Solution..."):
                parser.run(progress_callback=progress_update) #
            
            end = time.perf_counter()
            
            # --- SAVE TO STATE ---
            # We store the results so they survive the rerun
            st.session_state.reaction_time = round((end - start), 2)
            st.session_state.molecule_obj = parser # Save the whole parser object
            st.session_state.processed_df = parser.data_frame_gen() # Save the DF
            
            # Force a rerun so the app updates immediately to the "Display" phase
            st.rerun()

    # --- LOGIC BRANCH 2: Persistent Display ---
    # If data exists in memory, show it (this runs even after clicking Download)
    if st.session_state.processed_df is not None:
        
        # Retrieve our variables from state
        df = st.session_state.processed_df
        parser = st.session_state.molecule_obj # We retrieve the parser to check failed inputs
        total_time = st.session_state.reaction_time

<<<<<<< HEAD
        col1, col2 = st.columns(2)
        with col1:
            st.success("Compounds Cooked!!!!!")
        with col2:
            st.success(f"The Reaction took {total_time} Seconds")
=======
        status_text.write(f"{100 * round(percent)} % Reaction Done")
>>>>>>> 0132422490e74348a592848f131352b102430ecf

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

        # Check for failed inputs using the retrieved parser object
        if parser.failed_inputs:    
            st.warning(f"{len(parser.failed_inputs)} compounds failed, Kindly check the names or CIDs again")

            with st.expander("⚠️ View Failed Inputs"):
                for fail in parser.failed_inputs:
                    st.write(f"- {fail}")

        # --- Interactive Selection Logic ---
        st.divider()
        st.subheader("🧬 3D Structure Downloader")
        st.info("Select rows in the table above to generate SDF download buttons.")

        # 1. Update the dataframe to be interactive
        # We capture the output in a variable called 'event'
        event = st.dataframe(
            st.session_state.processed_df, # Use the DF from memory
            use_container_width=True,
            on_select="rerun",             # Reruns the script when a row is clicked
            selection_mode="multi-row",    # Allows picking more than one molecule
            key="data_table"               # Unique key is good practice
        )

        selected_rows = event.selection.rows

        if selected_rows:
            st.write(f"**Selected {len(selected_rows)} molecule(s):**")

            
        for row_index in selected_rows:
                # A. Retrieve the actual Molecule Object from the parser we saved
                # st.session_state.molecule_obj is your Parser instance
                # .molecules is the list inside it
                mol = st.session_state.molecule_obj.molecules[row_index]
                
                # B. Create a container for each selection
                with st.container(border=True):
                    col_info, col_btn = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**{mol.name}** (CID: {mol.cid})")
                    
                    with col_btn:
                        # C. Fetch the SDF data (This might take 1-2 seconds per button)
                        # We do this here so it only runs for SELECTED rows, not all 50!
                        sdf_data = mol.get_sdf()
                        
                        if sdf_data:
                            st.download_button(
                                label="⬇️ Download .SDF",
                                data=sdf_data,
                                file_name=f"{mol.name}_{mol.cid}.sdf",
                                mime="chemical/x-mdl-sdfile",
                                key=f"btn_{mol.cid}" # UNIQUE KEY is critical here!
                            )
                        else:
                            st.error("No 3D Data")


        # Add a Reset Button to clear state and allow new uploads
        st.divider()
        if st.button("🗑️ Wash the Beaker (Reset)"):
            st.session_state.processed_df = None
            st.session_state.molecule_obj = None
            st.rerun()