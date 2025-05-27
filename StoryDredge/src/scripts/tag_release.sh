#!/bin/bash
# tag_release.sh - Tag and push the release version to git

# Get version from version.json
VERSION=$(grep -o '"version": "[^"]*"' version.json | cut -d'"' -f4)

if [ -z "$VERSION" ]; then
  echo "Error: Unable to determine version from version.json"
  exit 1
fi

echo "Preparing to tag version $VERSION for release"
echo "========================================"

# Check for changes
if ! git diff --quiet; then
  echo "Warning: You have uncommitted changes. Please commit or stash them before tagging."
  read -p "Do you want to continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting."
    exit 1
  fi
fi

# Create an annotated tag
echo "Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Version $VERSION release"

# Show the created tag
echo "Tag created:"
git show "v$VERSION" --quiet

# Ask to push
read -p "Push tag to remote repository? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Pushing tag to remote..."
  git push origin "v$VERSION"
  echo "Tag v$VERSION pushed successfully!"
else
  echo "Tag created but not pushed. To push later, use:"
  echo "  git push origin v$VERSION"
fi

echo "Done!" 