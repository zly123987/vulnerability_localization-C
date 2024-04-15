# from unidiff import PatchSet
# import io

# # Load the patch content from a string or file
# patch_content = """--- a/file1.txt
# +++ b/file1.txt
# @@ -1,3 +1,4 @@
# +Added line to file1
#  Line 1
#  Line 2
#  Line 3
# --- a/file2.txt
# +++ b/file2.txt
# @@ -1,3 +1,4 @@
# +Added line to file2
#  Line A
#  Line B
#  Line C"""

# def apply_patch(repo_path, patch_content, cve):
#     patch_set = PatchSet(patch_content)

#     # Directory where the original files are located
#     original_files_dir = repo_path

#     # Directory where to save the patched files (can be the same as original_files_dir)
#     patched_files_dir = repo_path

#     # Iterate over each file in the patch set
#     for patched_file in patch_set:
#         # Construct the path to the original file and the path for the patched output
#         original_file_path = original_files_dir + '/' + patched_file.path
#         patched_file_path = patched_files_dir + '/' + patched_file.path.replace('.java', '_'+cve+'_patched.java')
#         print(patched_file_path)
#         # Read the original file content
#         with open(original_file_path, 'r') as file:
#             original_content = file.readlines()

#         # Apply the patch to the original content
#         patched_content = original_content
#         for hunk in patched_file:
#             hunk.apply_to(patched_content)

#         # Write the patched content to a file
#         with open(patched_file_path, 'w') as file:
#             file.writelines(patched_content)


