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
                self.is_valid = True
            else:
                print("Something went wrong!!!!!!")
                self.is_valid = False

        except Exception as e:
            print(f"Error Fetching : {self.user_input} : {e}")
            self.is_valid = False
        



    def to_dict(self):
        return {
            "name": self.name,
            "cid" : self.cid,
            "smiles" : self.smiles,
            "molecular_mass" : self.mol_mass,
            "molecular_formula" : self.mol_formula
        }


class MoleculeParser:


    def __init__(self, raw_txt):
        self.raw_txt = raw_txt
        self.clean_list = []
        self.molecules = []


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


    def run(self):
        self.cleaner()

        for item in self.clean_list:
            dtype = self._type_check(item)
            molecule_object = Molecule(item, dtype)
            molecule_object.get_data()
            self.molecules.append(molecule_object)

    def data_frame_gen(self):
        data = [m.to_dict() for m in self.molecules]
        df = pd.DataFrame(data)
        df.to_csv("my_dataframe", index=False)
        return df

if __name__ == "__main__":
    parser1 = MoleculeParser('Aspirine|Methane\tacetone,C=O|100,200|ethoxy,Salicyclic Acid')
    parser1.run()
    df = parser1.data_frame_gen()
    df.to_csv("my_df.csv", sep="\t", index=False)






