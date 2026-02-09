import pubchempy as pcp
import re
import pandas as pd
import time

class Molecule:

    def __init__(self, user_input, input_type):
        self.user_input = user_input
        self.input_type = input_type
        self.name = None
        self.cid = 0
        self.smiles = None
        self.mol_mass = None
        self.mol_formula = None
        self.is_valid = False
        self.h_donor = 0
        self.h_acceptor = 0
        self.logP = 0

    def get_data(self):

        try:
            compounds  = pcp.get_compounds(self.user_input, self.input_type)
            if compounds:
                compound = compounds[0]
                self.name = compound.iupac_name
                self.smiles = compound.smiles
                self.cid = compound.cid
                self.mol_mass = compound.molecular_weight
                self.mol_formula = compound.molecular_formula
                self.h_donor = compound.h_bond_donor_count
                self.h_acceptor = compound.h_bond_donor_count
                self.logP = compound.xlogp
                self.is_valid = True
            else:
                
                self.is_valid = False

        except Exception as e:
            print(f"Error Fetching : {self.user_input} : {e}")
            self.is_valid = False
        

    def get_sdf(self):
            if not self.is_valid or not self.cid:
                return None
            try:
                 return pcp.get_sdf(self.cid, "cid", record_type="3d")
            except Exception as e:
                return None

    def to_dict(self):
        return {
            "name": self.name,
            "cid" : self.cid,
            "smiles" : self.smiles,
            "molecular_mass" : self.mol_mass,
            "molecular_formula" : self.mol_formula,
            'logP' : self.logP,
            'H_donor_atoms' : self.h_donor,
            'H_acceptor_atoms' : self.h_acceptor
        }


        

class MoleculeParser:


    def __init__(self, raw_txt):
        self.raw_txt = raw_txt
        self.clean_list = []
        self.molecules = []
        self.failed_inputs = []


    def _type_check(self, token):
        if token.isdigit():
            return "cid"
        elif any(ch in token for ch in ['=', '#', '(', ')', '[', ']']):
            return "smiles"
        else:
            return 'name'


    def cleaner(self):
        tokens  = re.split(r'[|\n\t,]+', self.raw_txt)
        cleaned = [t.strip() for t in tokens if t.strip()]
        self.clean_list = list(dict.fromkeys(cleaned))


    def run(self, progress_callback=None):
        self.cleaner()
        self.clean_list = self.clean_list[:50] 
        total = len(self.clean_list)

        for index, item in enumerate(self.clean_list):
            dtype = self._type_check(item)
            molecule_object = Molecule(item, dtype)
            molecule_object.get_data()
            if molecule_object.is_valid:

                self.molecules.append(molecule_object)
            else:
                self.failed_inputs.append(item)



            # The Script will wait between calls 
            time.sleep(1.5)

            if progress_callback:
                progress_callback((index + 1) / total)

    def data_frame_gen(self):
        data = [m.to_dict() for m in self.molecules]
        df = pd.DataFrame(data)
        return df

if __name__ == "__main__":
    parser = MoleculeParser('Aspirine|Methane\tacetone,C=O|100,200|ethoxy,Salicyclic Acid')
    parser.run()
    df = parser.data_frame_gen()
    df.to_csv("my_df.csv", sep="\t", index=False)






