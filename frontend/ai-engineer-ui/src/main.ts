import { bootstrapApplication } from "@angular/platform-browser";
import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { HttpClient, provideHttpClient } from "@angular/common/http";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: ` <main>
    <header>
      <h1>TonyAI</h1>
      <span>v0.2 • Ollama / OpenRouter + .NET 10 + Python</span>
    </header>

    <section class="panel">
      <label>Task</label>
      <textarea
        [(ngModel)]="task"
        placeholder="Create a .NET 10 Employee CRUD API using EF Core and SQL Server"
      ></textarea>

      <div class="row">
        <label>
          Complexity
          <input
            type="number"
            min="1"
            max="10"
            [(ngModel)]="complexity"
          />
        </label>

        <label>
          Project
          <input [(ngModel)]="project" />
        </label>

        <button (click)="run()" [disabled]="loading">
          {{ loading ? "Running..." : "Run TonyAI" }}
        </button>
      </div>
    </section>

    <section class="panel">
      <h2>Agent Activity</h2>

      <div *ngIf="loading">
        <p>⏳ TonyAI is working...</p>
        <p>Waiting for the configured AI provider...</p>
      </div>

      <div *ngIf="result && !result.error">
        <p><b>Agent:</b> {{ result.agent }}</p>
        <p><b>Provider:</b> {{ result.provider || "ollama" }}</p>
        <p><b>Model:</b> {{ result.model }}</p>

        <h3>Output</h3>
        <pre>{{ result.result }}</pre>
      </div>

      <div *ngIf="result?.error">
        <h3>❌ Error</h3>
        <pre>{{ result.error }}</pre>
      </div>

      <p *ngIf="!result && !loading">No task executed yet.</p>
    </section>

    <section class="panel">
      <h2>System</h2>
      <button (click)="health()">Check AI Providers</button>
      <pre>{{ healthResult | json }}</pre>
    </section>
  </main>`,
  styles: [
    `
      main {
        max-width: 1100px;
        margin: 30px auto;
        padding: 0 20px;
        font-family: Arial;
      }
      body {
        margin: 0;
        background: #0e0e0e;
        color: #eee;
      }
      .panel {
        background: #171717;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
      }
      textarea {
        width: 100%;
        min-height: 140px;
        box-sizing: border-box;
        background: #0d0d0d;
        color: #eee;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 12px;
      }
      .row {
        display: flex;
        gap: 20px;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 15px;
      }
      input {
        background: #0d0d0d;
        color: #eee;
        border: 1px solid #444;
        padding: 8px;
      }
      button {
        padding: 10px 16px;
        border: 0;
        border-radius: 7px;
        cursor: pointer;
      }
      pre {
        white-space: pre-wrap;
        background: #0d0d0d;
        padding: 14px;
        border-radius: 8px;
      }
    `,
  ],
})
export class AppComponent {
  task = "";
  project = "default";
  complexity = 5;
  loading = false;
  result: any = null;
  healthResult: any = null;

  constructor(private http: HttpClient) {}

  run() {
    this.loading = true;
    this.result = null;

    this.http
      .post<any>("http://localhost:5000/api/task", {
        task: this.task,
        project: this.project,
        complexity: this.complexity,
      })
      .subscribe({
        next: (value) => {
          console.log("TONYAI RESPONSE:", value);
          this.result = value;
          this.loading = false;
        },
        error: (err) => {
          console.error("TONYAI ERROR:", err);

          this.result = {
            error:
              err.error?.detail ||
              err.error?.message ||
              err.message ||
              "Unknown error",
          };

          this.loading = false;
        },
      });
  }

  health() {
    this.http
      .get<any>("http://localhost:5000/api/health")
      .subscribe({
        next: (value) => (this.healthResult = value),
        error: (err) => {
          this.healthResult = {
            error:
              err.error?.detail ||
              err.error?.message ||
              err.message ||
              "Unable to reach the gateway",
          };
        },
      });
  }
}

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
}).catch(console.error);
