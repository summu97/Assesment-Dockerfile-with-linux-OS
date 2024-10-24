import os

def build_docker_image():
    # Ask the user for the image name and the Dockerfile path
    image_name = input("Enter the Docker image name to build: ")
    dockerfile_path = input("Enter the path to the Dockerfile: ")

    # Run docker images command to list Docker images
    print("\nFetching list of available Docker images...")
    images_result = os.popen("docker images --format '{{.Repository}}:{{.Tag}}'").readlines()
    existing_images = [img.strip() for img in images_result]

    # Check if the image name already exists
    if image_name in existing_images:
        version_suffix = 1
        new_image_name = f"{image_name}:{version_suffix}"
        while new_image_name in existing_images:
            version_suffix += 1
            new_image_name = f"{image_name}:{version_suffix}"
        image_name = new_image_name
        print(f"Image name already exists. Using new image name: {image_name}")

    # Construct the docker build command
    build_command = f"docker build -t {image_name} {dockerfile_path}"

    print(f"Running command: {build_command}")
    
    # Run the build command
    result = os.system(build_command)
    
    # Check if the build was successful
    if result == 0:
        print(f"Docker image built successfully with name: {image_name}")
    else:
        print("Failed to build the Docker image.")
        return

    # List all Docker images again after the build
    print("\nFetching updated list of Docker images...")
    updated_images_result = os.popen("docker images").readlines()

    if not updated_images_result:
        print("No Docker images found.")
        return

    # Display the list of images numerically, skipping the header
    print("\nAvailable Docker images:")
    images = updated_images_result[1:]  # Skip the header
    for index, image in enumerate(images, 1):
        print(f"{index}. {image.strip()}")

    # Ask the user to select an image by number
    selected_image_index = int(input("\nSelect an image number: ")) - 1
    if selected_image_index < 0 or selected_image_index >= len(images):
        print("Invalid image selection.")
        return

    # Get the selected image name (repository:tag)
    selected_image = images[selected_image_index].split()[0] + ":" + images[selected_image_index].split()[1]

    # Save the selected image as a .tar file
    tar_file_name = f"{selected_image.replace(':', '_')}.tar"
    save_command = f"docker save -o {tar_file_name} {selected_image}"

    print(f"Saving the image as {tar_file_name}...")
    result = os.system(save_command)

    if result == 0:
        print(f"Image saved successfully as {tar_file_name}")
    else:
        print(f"Failed to save the image {selected_image}.")
        return

    # Run gsutil ls command to list GCS buckets
    print("\nFetching list of GCS buckets...")
    buckets_result = os.popen("gsutil ls").readlines()

    if not buckets_result:
        print("No GCS buckets found.")
        return

    # Display the list of buckets numerically
    print("\nAvailable GCS buckets:")
    buckets = [bucket.strip() for bucket in buckets_result]
    for index, bucket in enumerate(buckets, 1):
        print(f"{index}. {bucket}")

    # Ask the user to select a bucket by number
    selected_bucket_index = int(input("\nSelect a bucket number: ")) - 1
    if selected_bucket_index < 0 or selected_bucket_index >= len(buckets):
        print("Invalid bucket selection.")
        return

    # Get the selected bucket name
    bucket_name = buckets[selected_bucket_index]

    # Construct the gsutil cp command to upload the .tar file
    upload_command = f"gsutil cp {tar_file_name} {bucket_name}"

    print(f"Uploading {tar_file_name} to {bucket_name}...")
    result = os.system(upload_command)

    if result == 0:
        print(f"{tar_file_name} uploaded successfully to {bucket_name}.")
    else:
        print(f"Failed to upload {tar_file_name} to {bucket_name}.")

if __name__ == "__main__":
    build_docker_image()
