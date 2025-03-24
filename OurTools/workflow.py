from OurTools.LLM.Langchain_test import LLM_analysis_commmit
from OurTools.utils import read_commitInfo





content = read_commitInfo("F:/download_space/2022-04/SIB_Smart_Resume")
LLM_analysis_commmit(content)
