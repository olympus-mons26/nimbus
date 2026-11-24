# Publish Nimbus through Homebrew

Nimbus's automatic release workflow publishes a macOS Apple Silicon archive and updates the Homebrew tap whenever a push to `main` succeeds. The tap must be initialized and its write token configured before pushing changes to `main`.

## One-time setup

### 1. Create the tap repository

Create a public GitHub repository named **`olympus-mons26/homebrew-tap`**. The workflow expects this exact repository.

Clone it and add a tracked `Formula` directory. Git does not track empty directories, so add a placeholder file:

```sh
git clone https://github.com/olympus-mons26/homebrew-tap.git
cd homebrew-tap
mkdir -p Formula
touch Formula/.gitkeep
git add Formula/.gitkeep
git commit -m "Initialize Homebrew tap"
git push origin main
```

The Nimbus workflow will create or replace `Formula/nimbus.rb` when it publishes a release.

### 2. Create a tap write token

Create a fine-grained personal access token in GitHub:

1. Open **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.
2. Select `olympus-mons26` as the resource owner.
3. Give the token access only to the `homebrew-tap` repository.
4. Grant **Contents: Read and write** permission.
5. Choose an expiration and create the token.

If GitHub requires organization approval for the token, complete that approval before continuing. Never put the token in source code or commit it.

### 3. Add the token to the Nimbus repository

In `olympus-mons26/nimbus`, open **Settings → Secrets and variables → Actions → New repository secret** and add:

- Name: `HOMEBREW_TAP_TOKEN`
- Secret: the fine-grained token from the previous step

The workflow uses the built-in `GITHUB_TOKEN` to create the Nimbus release. `HOMEBREW_TAP_TOKEN` is only used to push the formula to the separate tap repository.

## Publish a release

After tap setup and the secret are in place, push a commit to the `main` branch of `olympus-mons26/nimbus`. The `Nimbus Automatic Release` workflow then:

1. Runs the test suite.
2. Builds the `wf` executable on a macOS runner.
3. Creates a prerelease named `1.0.0-dev.<run number>` with a tar archive and SHA-256 checksum.
4. Generates `Formula/nimbus.rb` with the release URL and archive SHA-256.
5. Pushes the formula change to `olympus-mons26/homebrew-tap`.

Follow the run under the Nimbus repository's **Actions** tab. If `update-tap` fails, check that `Formula/.gitkeep` is on the tap's default branch, the `HOMEBREW_TAP_TOKEN` secret has access to that repository, and the token has not expired.

Each successful push to `main` creates a prerelease. This workflow does not publish a stable release, so avoid pushing unrelated commits to `main` after enabling the secret.

## Install Nimbus

Once the first workflow run succeeds and the formula commit is visible in the tap:

```sh
brew tap olympus-mons26/tap
brew install olympus-mons26/tap/nimbus
wf --version
wf London
```

The current Homebrew automation publishes **macOS Apple Silicon (arm64) only**. Intel Macs are not supported by this tap formula yet. The formula template in `installers/homebrew/nimbus.rb` is not a substitute for a successful release and contains placeholders rather than a usable checksum.

## Troubleshooting

- **Checkout of the tap fails:** Verify the tap repository name and `HOMEBREW_TAP_TOKEN` permissions.
- **Formula update fails because the directory is missing:** Ensure `Formula/.gitkeep` was committed to the tap's default branch.
- **`brew install` cannot find Nimbus:** Confirm `Formula/nimbus.rb` exists in the tap and that the Actions release completed successfully; then run `brew update`.
- **Checksum or download errors:** Open the generated formula and compare its release URL and SHA with the assets on the matching GitHub prerelease.
