var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("Orchestrator", client => {
    client.BaseAddress = new Uri(builder.Configuration["Orchestrator:BaseUrl"] ?? "http://127.0.0.1:8100");
    client.Timeout = TimeSpan.FromSeconds(30);
});
builder.Services.AddCors(o => o.AddPolicy("ui", p => p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));
var app = builder.Build();
app.UseCors("ui");

app.MapGet("/api/health", async (IHttpClientFactory f) =>
{
    var r = await f.CreateClient("Orchestrator").GetAsync("/health");
    return Results.Content(
        await r.Content.ReadAsStringAsync(),
        "application/json",
        statusCode: (int)r.StatusCode);
});

app.MapGet("/api/models", async (IHttpClientFactory f) =>
{
    var r = await f.CreateClient("Orchestrator").GetAsync("/models");
    return Results.Content(
        await r.Content.ReadAsStringAsync(),
        "application/json",
        statusCode: (int)r.StatusCode);
});

app.MapPost("/api/task", async (HttpRequest req, IHttpClientFactory f) =>
{
    using var sr = new StreamReader(req.Body);
    var body = await sr.ReadToEndAsync();

    using var m = new HttpRequestMessage(
        HttpMethod.Post,
        "/task")
    {
        Content = new StringContent(
            body,
            System.Text.Encoding.UTF8,
            "application/json")
    };

    var r = await f.CreateClient("Orchestrator").SendAsync(m);

    return Results.Content(
        await r.Content.ReadAsStringAsync(),
        "application/json",
        statusCode: (int)r.StatusCode);
});

app.MapGet("/api/task/{taskId}", async (string taskId, IHttpClientFactory f) =>
{
    var r = await f.CreateClient("Orchestrator").GetAsync($"/task/{taskId}");
    return Results.Content(
        await r.Content.ReadAsStringAsync(),
        "application/json",
        statusCode: (int)r.StatusCode);
});

app.Run();
