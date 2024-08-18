function readEntry(entryId) {
    fetch('/read', {
        method: 'POST',
        body: JSON.stringify({ entryId: entryId}),
    });
}