def extract_kaggle_username(user_input):
    user_input = user_input.strip()
    if "kaggle.com" in user_input:
        parts = user_input.rstrip('/').split('/')
        return parts[-1]
    return user_input

from kaggle.api.kaggle_api_extended import KaggleApi

def get_kaggle_notebooks(username):
    api = KaggleApi()
    api.authenticate()

    kernels = api.kernels_list(user=username)

    notebook_list = []
    for kernel in kernels:
        notebook_list.append({
            "title": kernel.title,
            "ref": kernel.ref,
            "language": kernel.language,
            "votes": getattr(kernel, "totalVotes", None)
        })
    return notebook_list

def get_kaggle_datasets(username):
    api = KaggleApi()
    api.authenticate()

    datasets = api.dataset_list(user=username)

    dataset_list = []
    for dataset in datasets:
        dataset_list.append({
            "title": dataset.title,
            "ref": dataset.ref,
            "size": getattr(dataset, "totalBytes", None)
        })
    return dataset_list

def get_kaggle_summary(user_input):
    username = extract_kaggle_username(user_input)
    notebooks = get_kaggle_notebooks(username)
    datasets = get_kaggle_datasets(username)

    return {
        "username": username,
        "notebook_count": len(notebooks),
        "notebooks": notebooks,
        "dataset_count": len(datasets),
        "datasets": datasets
    }