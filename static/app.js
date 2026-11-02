const state = { token: localStorage.getItem('focus_token'), username: localStorage.getItem('focus_user'), todos: [], filter: 'all', editing: null };
const $ = (id) => document.getElementById(id);
const statusMessages = { 400: 'The request could not be understood.', 401: 'Your session has expired. Please sign in again.', 403: 'You do not have permission to do that.', 404: 'The requested item was not found.', 409: 'This item already exists.', 422: 'Please check the highlighted fields.', 500: 'The server encountered an error.' };
const formatError = (error) => error instanceof TypeError ? 'Unable to reach the server. Check your connection and try again.' : (error?.message || 'Something went wrong. Please try again.');
const formatDetail = (detail) => Array.isArray(detail) ? detail.map((item) => item.msg || item.message || String(item)).join(' ') : (typeof detail === 'object' && detail !== null ? detail.message || JSON.stringify(detail) : detail ? String(detail) : '');
const api = async (path, options = {}) => {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let message = statusMessages[response.status] || `Request failed (HTTP ${response.status}).`;
    try { const body = await response.json(); message = formatDetail(body.detail) || message; } catch (_) {}
    if (response.status === 401) logout();
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
};
const show = (id, visible) => $(id).classList.toggle('hidden', !visible);
const toast = (message) => { $('toast').textContent = message; $('toast').classList.add('show'); setTimeout(() => $('toast').classList.remove('show'), 2200); };
function logout() { state.token = null; localStorage.removeItem('focus_token'); show('app-view', false); show('auth-view', true); }
function setAuthMode(register) {
  $('auth-title').textContent = register ? 'Create your Focus account' : 'Everything important, at hand';
  $('auth-subtitle').textContent = register ? 'It only takes a minute to get started.' : 'Sign in to manage your tasks.';
  $('email-field').classList.toggle('hidden', !register);
  $('auth-email').required = register;
  $('auth-submit').textContent = register ? 'Create account' : 'Sign in';
  $('auth-toggle').textContent = register ? 'I already have an account' : 'Create an account';
  $('auth-form').dataset.register = register;
}
async function authenticate(event) {
  event.preventDefault(); $('auth-error').textContent = '';
  const register = $('auth-form').dataset.register === 'true';
  const username = $('auth-username').value.trim(), password = $('auth-password').value;
  try {
    if (register) {
      await api('/auth/create_user', { method: 'POST', body: JSON.stringify({ username, email: $('auth-email').value.trim() || null, password }) });
    }
    const result = await api('/auth/login-page', { method: 'POST', body: JSON.stringify({ username, email: null, password }) });
    state.token = result.access_token; state.username = username;
    localStorage.setItem('focus_token', state.token); localStorage.setItem('focus_user', username);
    show('auth-view', false); show('app-view', true); $('user-name').textContent = username; await loadTodos();
  } catch (error) { $('auth-error').textContent = formatError(error); }
}
async function loadTodos() {
  $('list-message').textContent = 'Loading tasks…';
  try { const result = await api('/todos/todos'); state.todos = Array.isArray(result['Your todos']) ? result['Your todos'] : []; }
  catch (error) { $('list-message').textContent = formatError(error); $('task-list').innerHTML = ''; return; }
  render();
}
function render() {
  const query = $('search').value.toLowerCase();
  const filtered = state.todos.filter((todo) => (state.filter === 'all' || (state.filter === 'done' ? todo.done : !todo.done)) && `${todo.name} ${todo.description}`.toLowerCase().includes(query));
  $('total-count').textContent = state.todos.length; $('done-count').textContent = state.todos.filter((todo) => todo.done).length; $('open-count').textContent = state.todos.filter((todo) => !todo.done).length;
  $('list-message').textContent = filtered.length ? '' : (state.todos.length ? 'No tasks match your search.' : 'No tasks yet — add your first one.');
  $('task-list').innerHTML = filtered.map((todo) => `<article class="task ${todo.done ? 'done' : ''}"><input class="task-check" type="checkbox" data-action="toggle" data-id="${todo.user_task_number}" ${todo.done ? 'checked' : ''}><div><div class="task-name">${escapeHtml(todo.name)}</div><p class="task-description">${escapeHtml(todo.description)}</p>${(todo.tags || []).map((tag) => `<span class="tag ${tag.color}">${escapeHtml(tag.name)}</span>`).join('')}</div><div class="task-actions"><button class="icon-button" data-action="edit" data-id="${todo.user_task_number}" aria-label="Edit">✎</button><button class="icon-button" data-action="delete" data-id="${todo.user_task_number}" aria-label="Delete">×</button></div></article>`).join('');
}
function escapeHtml(value) { return String(value || '').replace(/[&<>"']/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;' }[char])); }
function openEditor(todo = null) { state.editing = todo; $('editor-title').textContent = todo ? 'Edit task' : 'New task'; $('task-name').value = todo?.name || ''; $('task-description').value = todo?.description || ''; $('task-importance').value = todo?.importance ?? 5; $('importance-value').textContent = $('task-importance').value; $('task-done').checked = Boolean(todo?.done); $('task-tag').value = todo?.tags?.[0]?.name || ''; $('task-color').value = todo?.tags?.[0]?.color || 'BLUE'; show('editor', true); $('task-name').focus(); }
async function saveTask(event) {
  event.preventDefault(); $('task-error').textContent = '';
  const payload = { todo_request: { name: $('task-name').value.trim(), description: $('task-description').value.trim(), done: $('task-done').checked, importance: Number($('task-importance').value), tags: [] }, tag: { name: $('task-tag').value.trim() || 'General', color: $('task-color').value } };
  try { await api(state.editing ? `/todos/change/item_id${state.editing.user_task_number}` : '/todos/addtodo', { method: state.editing ? 'PUT' : 'POST', body: JSON.stringify(payload) }); show('editor', false); toast(state.editing ? 'Task updated' : 'Task added'); await loadTodos(); }
  catch (error) { $('task-error').textContent = formatError(error); }
}
async function handleTaskAction(event) {
  const control = event.target.closest('[data-action]'); if (!control) return;
  const todo = state.todos.find((item) => item.user_task_number === Number(control.dataset.id));
  if (!todo) return;
  try {
    if (control.dataset.action === 'edit') openEditor(todo);
    if (control.dataset.action === 'delete' && confirm('Delete this task?')) { await api(`/todos/delete/todo:${todo.user_task_number}`, { method: 'DELETE' }); toast('Task deleted'); await loadTodos(); }
    if (control.dataset.action === 'toggle') { const payload = { todo_request: { name: todo.name, description: todo.description, done: control.checked, importance: todo.importance, tags: [] }, tag: { name: todo.tags?.[0]?.name || 'General', color: todo.tags?.[0]?.color || 'BLUE' } }; await api(`/todos/change/item_id${todo.user_task_number}`, { method: 'PUT', body: JSON.stringify(payload) }); await loadTodos(); }
  } catch (error) { toast(formatError(error)); render(); }
}
$('auth-form').addEventListener('submit', authenticate); $('auth-toggle').addEventListener('click', () => setAuthMode($('auth-form').dataset.register !== 'true')); $('logout').addEventListener('click', logout); $('new-task').addEventListener('click', () => openEditor()); $('close-editor').addEventListener('click', () => show('editor', false)); $('task-form').addEventListener('submit', saveTask); $('task-list').addEventListener('click', handleTaskAction); $('task-list').addEventListener('change', handleTaskAction); $('search').addEventListener('input', render); $('task-importance').addEventListener('input', () => $('importance-value').textContent = $('task-importance').value); document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => { document.querySelector('.filter.active').classList.remove('active'); button.classList.add('active'); state.filter = button.dataset.filter; render(); }));
if (state.token) { show('auth-view', false); show('app-view', true); $('user-name').textContent = state.username || ''; loadTodos(); } else setAuthMode(false);
