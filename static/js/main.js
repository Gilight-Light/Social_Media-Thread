let loadingModal;
let currentTaskId = null;
let statusCheckInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        loadingModal = new bootstrap.Modal(modalElement);
    }
});

function showLoadingBrief(text = 'Processing...') {
    document.getElementById('loadingText').textContent = text;
    loadingModal.show();
}

function hideLoading() {
    loadingModal.hide();
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

function displayStatus(containerId, status, message, type = 'info') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Container not found:', containerId);
        return;
    }
    
    const alertClass = type === 'success' ? 'alert alert-success' : 
                      type === 'error' ? 'alert alert-danger' : 
                      type === 'warning' ? 'alert alert-warning' : 'alert alert-info';
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    container.innerHTML = `
        <div class="${alertClass}">
            <i class="${icon}"></i> ${message}
        </div>
    `;
}

function checkTaskStatus(taskId, containerId, onComplete = null) {
    fetch(`/task_status/${taskId}`)
        .then(response => response.json())
        .then(result => {
            if (result.status === 'running') {
                document.getElementById('loadingText').textContent = result.message || 'Processing...';
            } else if (result.status === 'success') {
                hideLoading();
                displayStatus(containerId, result.status, result.message, 'success');
                if (onComplete) onComplete(result);
                setTimeout(updateDataInfo, 1000);
            } else if (result.status === 'error') {
                hideLoading();
                displayStatus(containerId, result.status, result.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error checking task status:', error);
        });
}

async function filterPosts() {
    const btn = document.getElementById('filterPostsBtn');
    const symptomGroup = document.getElementById('symptomGroupSelect').value.trim();
    
    console.log(`[DEBUG] filterPosts called with: "${symptomGroup}"`);
    
    if (!symptomGroup) {
        displayStatus('filterPostsStatus', 'error', 'Please select a symptom group', 'error');
        return;
    }
    
    // Disable button and show loading
    btn.disabled = true;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Filtering...';
    
    try {
        console.log(`[DEBUG] Sending POST to /filter_posts`);
        
        const response = await fetch('/filter_posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptom_group: symptomGroup
            })
        });
        
        console.log(`[DEBUG] Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log(`[DEBUG] Response data:`, result);
        
        if (result.status === 'success') {
            displayStatus('filterPostsStatus', 'success', result.message, 'success');
            displayFilterResults(result.data);
            
            // Automatically refresh the Main Post Data view with filtered results
            setTimeout(() => {
                console.log('[DEBUG] Auto-refreshing main post view with filtered data');
                viewMainPost();
            }, 500);
            
        } else if (result.status === 'warning') {
            displayStatus('filterPostsStatus', 'warning', result.message, 'warning');
        } else {
            displayStatus('filterPostsStatus', 'error', result.message, 'error');
        }
        
    } catch (error) {
        console.error('[DEBUG] Error in filterPosts:', error);
        displayStatus('filterPostsStatus', 'error', `Error: ${error.message}`, 'error');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}

function displayFilterResults(data) {
    console.log(`[DEBUG] displayFilterResults called with:`, data);
    
    const resultsArea = document.getElementById('resultsArea');
    
    if (!data || !data.posts || data.posts.length === 0) {
        resultsArea.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> No posts found
            </div>
        `;
        return;
    }
    
    const posts = data.posts;
    console.log(`[DEBUG] Displaying ${posts.length} posts`);
    
    resultsArea.innerHTML = `
        <h5><i class="fas fa-filter"></i> Filter Results</h5>
        <div class="alert alert-success">
            <strong>Symptom Group:</strong> ${data.symptom_group} | 
            <strong>Posts Found:</strong> ${data.posts_count}
        </div>
        
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Username</th>
                        <th>Text</th>
                        <th>Timestamp</th>
                        <th>Keyword</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
                    ${posts.slice(0, 20).map(post => `
                        <tr>
                            <td><strong>${post.username || 'N/A'}</strong></td>
                            <td>
                                <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">
                                    ${(post.text || '').substring(0, 150)}${(post.text || '').length > 150 ? '...' : ''}
                                </div>
                            </td>
                            <td>${post.timestamp || 'N/A'}</td>
                            <td><span class="badge bg-primary">${post.keyword || 'N/A'}</span></td>
                            <td>
                                ${post.url ? `<a href="${post.url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-external-link-alt"></i> View
                                </a>` : 'N/A'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        ${posts.length > 20 ? `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> Showing first 20 of ${posts.length} posts. 
                Full data saved to: ${data.output_file}
            </div>
        ` : ''}
    `;
}

async function startUsersCrawl() {
    const btn = document.getElementById('crawlUsersBtn');
    
    console.log(`[DEBUG] startUsersCrawl called for filtered posts`);
    
    if (!btn) {
        console.error('Crawl users button not found');
        return;
    }
    
    // Check if filtered posts exist first
    try {
        const checkResponse = await fetch('/view_main_post');
        const checkResult = await checkResponse.json();
        
        if (!checkResult.is_filtered) {
            displayStatus('usersCrawlStatus', 'warning', 'Please filter posts first before crawling users', 'warning');
            return;
        }
    } catch (error) {
        displayStatus('usersCrawlStatus', 'error', 'Error checking filtered posts', 'error');
        return;
    }
    
    btn.disabled = true;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Crawling Users...';
    
    try {
        console.log('[DEBUG] Sending POST to /start_users_crawl');
        
        const response = await fetch('/start_users_crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log(`[DEBUG] Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('[DEBUG] Users crawl response:', result);
        
        if (result.status === 'success') {
            displayStatus('usersCrawlStatus', 'success', result.message, 'success');
            displayUsersCrawlResults(result.data);
        } else {
            displayStatus('usersCrawlStatus', 'error', result.message, 'error');
        }
        
    } catch (error) {
        console.error('[DEBUG] Error in startUsersCrawl:', error);
        displayStatus('usersCrawlStatus', 'error', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}

function displayUsersCrawlResults(data) {
    console.log('[DEBUG] displayUsersCrawlResults called with:', data);
    
    const resultsArea = document.getElementById('resultsArea');
    
    if (!data) {
        resultsArea.innerHTML = '<div class="alert alert-warning">No crawl results available.</div>';
        return;
    }
    
    resultsArea.innerHTML = `
        <h5><i class="fas fa-users"></i> Users Crawl Results</h5>
        
        <div class="row mb-3">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body text-center">
                        <h4>${data.total_users}</h4>
                        <small>Total Users</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <h4>${data.successful_crawls}</h4>
                        <small>Successful</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-danger text-white">
                    <div class="card-body text-center">
                        <h4>${data.failed_crawls}</h4>
                        <small>Failed</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <h4>${data.total_posts || 0}</h4>
                        <small>Total Posts</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> 
            <strong>Output File:</strong> ${data.output_file}<br>
            <strong>Crawled Users:</strong> ${data.usernames.join(', ')}
        </div>
        
        <div class="d-flex gap-2">
            <button class="btn btn-success" onclick="viewUserHistoryData()">
                <i class="fas fa-table"></i> View Crawled Data
            </button>
            <button class="btn btn-secondary" onclick="downloadUserHistory()">
                <i class="fas fa-download"></i> Download CSV
            </button>
        </div>
    `;
}

async function viewUserHistoryData() {
    try {
        console.log('[DEBUG] Viewing user history data');
        
        // Check if file exists by trying to fetch it
        const response = await fetch('/view_user_history');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('[DEBUG] User history response:', result);
        
        if (result.status === 'success') {
            displayTableData('User History Data', result.data, [
                'username', 'post_text', 'timestamp', 'url', 'crawl_date'
            ]);
        } else {
            displayStatus('resultsArea', 'error', result.message, 'error');
        }
        
    } catch (error) {
        console.error('[DEBUG] Error viewing user history:', error);
        displayStatus('resultsArea', 'error', `Error: ${error.message}`, 'error');
    }
}

function downloadUserHistory() {
    window.open('/download_user_history', '_blank');
}

async function updateDataInfo() {
    try {
        const response = await fetch('/get_data_info');
        if (response.ok) {
            location.reload();
        }
    } catch (error) {
        console.error('Error updating data info:', error);
    }
}

async function viewMainPost() {
    try {
        console.log('[DEBUG] viewMainPost called');
        const response = await fetch('/view_main_post');
        const result = await response.json();
        
        console.log('[DEBUG] viewMainPost response:', result);
        
        if (result.status === 'success') {
            let title = 'Main Post Data';
            if (result.is_filtered && result.filtered_symptom) {
                title = `Filtered Posts - ${result.filtered_symptom}`;
            }
            
            displayTableData(title, result.data, [
                'username', 'text', 'timestamp', 'url', 'symptom_group', 'keyword'
            ]);
            
            // Update the status in the results area header
            const resultsArea = document.getElementById('resultsArea');
            if (result.is_filtered) {
                resultsArea.innerHTML = `
                    <div class="alert alert-info mb-3">
                        <i class="fas fa-filter"></i> Currently showing filtered results for: <strong>${result.filtered_symptom || 'selected symptom group'}</strong>
                        <button class="btn btn-sm btn-outline-secondary ms-2" onclick="clearFilter()">
                            <i class="fas fa-times"></i> Clear Filter
                        </button>
                    </div>
                ` + resultsArea.innerHTML;
            }
            
        } else {
            displayStatus('resultsArea', 'error', result.message, 'error');
        }
    } catch (error) {
        console.error('[DEBUG] Error in viewMainPost:', error);
        displayStatus('resultsArea', 'error', `Error: ${error.message}`, 'error');
    }
}

// Add function to clear filter
async function clearFilter() {
    try {
        // Delete the filtered file if it exists
        const response = await fetch('/clear_filter', { method: 'POST' });
        if (response.ok) {
            displayStatus('filterPostsStatus', 'info', 'Filter cleared', 'info');
            viewMainPost(); // Refresh to show all data
        }
    } catch (error) {
        console.error('Error clearing filter:', error);
    }
}

async function viewUsersData() {
    try {
        console.log('[DEBUG] viewUsersData called');
        const response = await fetch('/view_users_data');
        const result = await response.json();
        
        console.log('[DEBUG] viewUsersData response:', result);
        
        if (result.status === 'success') {
            if (result.data_type === 'users_summary') {
                displayTableData('Users History Data', result.data, [
                    'username', 'total_posts', 'sample_post', 'latest_post', 'oldest_post'
                ]);
            } else {
                displayTableData('Users Data', result.data, [
                    'username', 'full_name', 'followers', 'posts_count', 'verified'
                ]);
            }
        } else {
            displayStatus('resultsArea', result.status, result.message, result.status);
        }
    } catch (error) {
        console.error('[DEBUG] Error in viewUsersData:', error);
        displayStatus('resultsArea', 'error', `Error: ${error.message}`, 'error');
    }
}

function displayTableData(title, data, columns) {
    const resultsArea = document.getElementById('resultsArea');
    
    if (!data || data.length === 0) {
        resultsArea.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> No data available for ${title}
            </div>
        `;
        return;
    }
    
    resultsArea.innerHTML = `
        <h5><i class="fas fa-table"></i> ${title}</h5>
        <div class="alert alert-info mb-3">
            <i class="fas fa-info-circle"></i> 
            <strong>Total Records:</strong> ${data.length}
            ${data[0].total_posts !== undefined ? ` | <strong>Total Posts:</strong> ${data.reduce((sum, item) => sum + (item.total_posts || 0), 0)}` : ''}
        </div>
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        ${columns.map(col => `<th>${col.replace(/_/g, ' ').toUpperCase()}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.slice(0, 50).map(row => `
                        <tr>
                            ${columns.map(col => {
                                let value = row[col] || 'N/A';
                                
                                // Handle different column types
                                if (col === 'url' && value !== 'N/A') {
                                    value = `<a href="${value}" target="_blank" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-external-link-alt"></i> View
                                    </a>`;
                                } else if ((col === 'text' || col === 'sample_post' || col === 'latest_post' || col === 'oldest_post') && typeof value === 'string' && value.length > 80) {
                                    value = `<span title="${value}" class="text-truncate d-inline-block" style="max-width: 300px;">
                                        ${value.substring(0, 80)}...
                                    </span>`;
                                } else if (col === 'username') {
                                    value = `<strong class="text-primary">${value}</strong>`;
                                } else if (col === 'total_posts') {
                                    value = `<span class="badge bg-success">${value}</span>`;
                                } else if (col === 'symptom_group') {
                                    value = `<span class="badge bg-info">${value}</span>`;
                                } else if (typeof value === 'string' && value.length > 100) {
                                    value = `<span title="${value}" class="text-truncate d-inline-block" style="max-width: 250px;">
                                        ${value.substring(0, 100)}...
                                    </span>`;
                                }
                                
                                return `<td>${value}</td>`;
                            }).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ${data.length > 50 ? `
            <div class="alert alert-secondary">
                <i class="fas fa-info-circle"></i> Showing first 50 of ${data.length} records
            </div>
        ` : ''}
    `;
}