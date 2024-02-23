import asyncio
import gists
import platform
import pathlib
import os
import shutil
import logging

logger = logging.getLogger(__name__)
client = gists.Client()


def save_gist_pub_keys_to_auth(pub_keys: str, dry_run: bool):
    authorized_keys_path = pathlib.Path.home().joinpath(".ssh/authorized_keys")
    if not authorized_keys_path.exists():
        if not authorized_keys_path.parent.exists():
            logger.info(f"Creating folder {authorized_keys_path.parent}")
            if not dry_run:
                authorized_keys_path.parent.mkdir(exist_ok=True)

        logger.info(f"Writing following pub_keys to {authorized_keys_path.absolute()}")
        logger.info(pub_keys)
        if not dry_run:
            authorized_keys_path.write_text(pub_keys)
        return
    logger.info(f"Appending following pub_keys to {authorized_keys_path.absolute()}")
    logger.info(pub_keys)
    if dry_run:
        return
    apply_pub_keys_to_file(authorized_keys_path, pub_keys)


def apply_pub_keys_to_file(authorized_keys_path: pathlib.Path, pub_keys: str):
    all_content = authorized_keys_path.read_text()
    start_sign = "# Pubauth Start(do not edit)"
    end_sign = "# Pubauth End(do not edit)"
    if start_sign in all_content and end_sign in all_content:
        start_idx = all_content.find(start_sign) + len(start_sign)
        end_idx = all_content.find(end_sign)
        contents = [all_content[:start_idx], pub_keys, all_content[end_idx:]]
    else:
        contents = [all_content, start_sign, pub_keys, end_sign]

    all_content = "\n".join(contents)
    shutil.copy2(authorized_keys_path, authorized_keys_path.with_suffix(".pubkey-bak"))
    authorized_keys_path.write_text(all_content)


def detect_pubkey():
    local_pub_key_name = os.getenv("PUB_KEY_FILE")
    if local_pub_key_name is not None:
        user_specify_path = pathlib.Path(local_pub_key_name)
        if not user_specify_path.exists() or not user_specify_path.is_file():
            logger.error(
                "The pubkey you specified is a not valid file or not exists yet"
            )
            return None
        return user_specify_path

    ssh_config_folder = pathlib.Path.home().joinpath(".ssh")
    for candidate in ["id_ed25519.pub", "id_rsa.pub"]:
        pubkey = ssh_config_folder.joinpath(candidate)
        if pubkey.exists() and pubkey.is_file():
            return pubkey
    logger.error("no pubkey founded in ~/.ssh named id_ed25519.pub nor id_rsa.pub")
    return None


async def upload_local_pubkey(gist_auth: str, gist: gists.Gist):
    gist_file = gist.files[0]
    current_content = gist_file.content

    if gist_auth is None:
        logger.error("No Gist Auth key provided.")
        return
    await client.authorize(gist_auth)
    logger.info(f"Authorized as {gist_auth[:-8]}{'x' * 8}")

    pubkey_path = detect_pubkey()
    if pubkey_path is None:
        logger.error("Stop now.")
        return
    with open(pubkey_path, "r") as local_key:
        content = local_key.read()
        if content in current_content:
            logger.info("Local pubkey is listed in remote pubkey skipping upload")
            return
        current_content += "\n"
        current_content += content
        await gist.edit(
            files=[gists.File(name=gist_file.name, content=current_content)]
        )


async def main():
    gist_id = os.getenv("GIST_ID")
    gist_auth = os.getenv("GIST_AUTH")
    if gist_id is None:
        logger.error("env GIST_ID is not provided")
        return
    logger.info(f"Using Gist Id {gist_id}")

    gist = await client.get_gist(gist_id)
    assert len(gist.files) == 1
    content = gist.files[0].content
    save_gist_pub_keys_to_auth(content, False)
    if gist_auth is not None:
        await upload_local_pubkey(gist_auth, gist)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
