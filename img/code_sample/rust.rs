#[cfg(windows)]
#[inline]
pub fn check_is_symlink(file_path: &str) -> bool {
    let symlink_metadata = match fs::symlink_metadata(file_path) {
        Ok(result) => result,
        Err(_) => return true,
    };

    symlink_metadata.file_attributes() == 1040
}