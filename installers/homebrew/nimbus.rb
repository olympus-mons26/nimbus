# Template only: the automatic release workflow generates the installable tap formula.
class Nimbus < Formula
  desc "A command-line weather reporter"
  homepage "https://github.com/olympus-mons26/nimbus"
  url "https://github.com/olympus-mons26/nimbus/releases/download/REPLACE_WITH_VERSION/nimbus-macos-arm64.tar.gz"
  sha256 "REPLACE_WITH_RELEASE_SHA256"
  version "REPLACE_WITH_VERSION"

  depends_on :macos
  depends_on arch: :arm64

  def install
    bin.install "wf"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/wf --version")
  end
end
