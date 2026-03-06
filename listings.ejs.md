```{=html}
<div class="quarto-listing quarto-listing-container-grid">
  <div class="list grid quarto-listing-cols-3">
<% for (const item of items) { %>
    <div class="g-col-1 quarto-grid-item card h-100" <%- metadataAttrs(item) %>>
<% if (item.image) { %>
      <img src="<%- item.image %>" class="card-img-top" style="height: 250px; object-fit: contain; background-color: #f8f9fa; padding: 10px;">
<% } %>
      <div class="card-body d-flex flex-column">
        <div>
          <h5 class="card-title"><a href="<%- item.path %>"><%= item.title %></a></h5>
<% if (item.subtitle) { %>
          <h6 class="card-subtitle text-muted mb-2"><%= item.subtitle %></h6>
<% } %>
<% if (item.description) { %>
          <p class="card-text"><%= item.description %></p>
<% } %>
        </div>
        <div class="mt-auto pt-3">
<% if (item.dashboard) { %>
          <a href="<%- item.dashboard %>" class="btn btn-success btn-sm me-1">Dashboard</a>
<% } %>
          <a href="<%- item.repo %>" class="btn btn-primary btn-sm">Repo</a>
        </div>
      </div>
    </div>
<% } %>
  </div>
</div>
```
