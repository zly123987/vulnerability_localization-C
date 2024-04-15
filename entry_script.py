from scripts.get_nvd_feed import get_info_all, get_info_by_cves
from scripts.get_xxx_data import get_data
from scripts.flatten_files_4_blizzard import flatten_files_4_blizzard
from scripts.organize_all_docs import organize_all_docs_for_tf_idf
from scripts.violin_supporting import plot_violin, violin_statistics

# get_data()
# flatten_files_4_blizzard('logging-log4j2')
get_info_all()
# organize_all_docs_for_tf_idf()
# get_info_by_cves()
# violin_statistics()
# plot_violin()