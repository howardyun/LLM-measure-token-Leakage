
# 定义 FileChange 类
class FileChange:
    def __init__(self, old_file, new_file, old_index, new_index, code_diff):
        self.old_file = old_file
        self.new_file = new_file
        self.old_index = old_index
        self.new_index = new_index
        self.code_diff = code_diff

    def __repr__(self):
        return f"FileChange(old_file={self.old_file}, new_file={self.new_file}, old_index={self.old_index}, new_index={self.new_index})"

# 定义 Commit 类
class Commit:
    def __init__(self, commit_hash, author, author_date, committer, commit_date, message):
        self.commit_hash = commit_hash
        self.author = author
        self.author_date = author_date
        self.committer = committer
        self.commit_date = commit_date
        self.message = message
        self.file_changes = []  # 存放 FileChange 对象列表

    def add_file_change(self, file_change):
        self.file_changes.append(file_change)

    def __repr__(self):
        return f"Commit(commit_hash={self.commit_hash}, author={self.author}, files_changed={len(self.file_changes)})"