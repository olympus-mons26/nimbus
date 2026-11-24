# Template only: replace the URL and SHA256 with values from an actual release.
# This formula is not yet published in a Homebrew tap.
class NimbusWeatherCli < Formula
  desc "A friendly weather forecast CLI"
  homepage "https://github.com/olympus-mons26/nimbus"
  url "https://github.com/olympus-mons26/nimbus/releases/download/v1.0.0/wf-macos-arm64.tar.gz"
  sha256 "REPLACE_WITH_RELEASE_SHA256"
  version "1.0.0"

  def install
    bin.install "wf"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/wf --version")
  end
end
