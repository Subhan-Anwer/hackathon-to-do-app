# Spec Writer Skill

A comprehensive skill for generating Spec-Kit Plus compliant specifications for full-stack web applications.

## Overview

This skill helps Claude generate complete, implementation-ready specifications following Spec-Kit Plus conventions. The generated specs are designed to be read and implemented directly by backend builders, frontend builders, and database designers.

## When to Use

Use this skill when you need to:
- Create project specifications from scratch
- Document features, APIs, database schemas, or UI components
- Start a new spec-driven development project
- Generate specs for hackathons or rapid development projects

## What This Skill Generates

### Project-Level Specifications
- **overview.md** - Project summary, tech stack, features, timeline
- **api-spec.md** - Complete API documentation with endpoints, examples, errors
- **database-schema.md** - Database design with tables, relationships, migrations
- **ui-components.md** - Frontend component specifications

### Feature-Level Specifications
- **spec.md** - Feature requirements and acceptance criteria
- **plan.md** - Architecture decisions and implementation approach
- **tasks.md** - Actionable implementation tasks

## Quick Start

Simply invoke the spec-writer skill:

```
/spec-writer
```

Or ask Claude to create specs:
```
Create comprehensive specs for a todo application
```

Claude will:
1. Ask targeted questions about your project
2. Generate all necessary spec files
3. Validate for consistency and completeness
4. Suggest next steps

## Skill Contents

### Templates (assets/)
Ready-to-use templates for all spec types:
- `overview-template.md` - Project overview structure
- `api-spec-template.md` - API documentation template
- `database-schema-template.md` - Database design template
- `feature-spec-template.md` - Feature requirements template

### Conventions (references/)
- `spec-kit-conventions.md` - Complete style guide including:
  - File naming conventions (lowercase-with-hyphens)
  - Document structure standards
  - Cross-referencing patterns
  - Code example formatting
  - Anti-patterns to avoid

### Scripts (scripts/)
- `validate-specs.py` - Automated validation tool that checks:
  - Template placeholders removed
  - Cross-references valid
  - Consistency across specs
  - Required sections present

## Example Usage

**User:** "Create specs for a full-stack todo app with Next.js and FastAPI"

**Claude will:**
1. Ask about tech stack details (database, auth, hosting)
2. Confirm core features (CRUD operations, filtering, etc.)
3. Generate `/specs/` directory with:
   - `overview.md` - Todo app project summary
   - `api-spec.md` - Auth + CRUD endpoints
   - `database-schema.md` - Users + Todos tables
   - `todo-management/spec.md` - Feature requirements
4. Validate all specs for consistency
5. Suggest running validation script and next steps

## Validation

After specs are generated, validate them:

```bash
python3 .claude/skills/spec-writer/scripts/validate-specs.py specs/
```

The validation script checks for:
- ✅ No template placeholders remaining
- ✅ All cross-references point to valid files
- ✅ Consistent terminology throughout
- ✅ Required sections present
- ✅ API endpoints match database schema

## Best Practices Enforced

This skill enforces these best practices:

1. **Specificity** - Concrete requirements, not vague descriptions
2. **Consistency** - Same terminology across all specs
3. **Completeness** - Error scenarios, validation rules, examples
4. **Cross-references** - Linked specs for easy navigation
5. **Examples** - Code samples for all APIs and schemas
6. **Validation** - Clear acceptance criteria

## Hackathon Context

This skill is optimized for the Phase II hackathon building a full-stack todo application with:
- **Frontend:** Next.js 16+ (App Router)
- **Backend:** Python FastAPI
- **Database:** PostgreSQL (Neon) with SQLModel ORM
- **Auth:** Better Auth with JWT
- **Features:** CRUD operations, completion status, filtering

The skill includes pre-configured examples and templates tailored to this tech stack.

## File Structure Generated

```
specs/
├── overview.md              # Project overview
├── architecture.md          # System architecture
├── database-schema.md       # Database design
├── api-spec.md              # API endpoints
├── ui-components.md         # Frontend components
└── <feature-name>/
    ├── spec.md              # Feature requirements
    ├── plan.md              # Architecture decisions
    └── tasks.md             # Implementation tasks
```

## Next Steps After Spec Generation

1. **Review** - Verify specs match requirements
2. **Validate** - Run `validate-specs.py`
3. **Plan** - Generate implementation plan with `/sp.plan`
4. **Tasks** - Create actionable tasks with `/sp.tasks`
5. **Implement** - Begin development

## Package Contents

```
spec-writer/
├── SKILL.md                           # Main skill instructions
├── README.md                          # This file
├── assets/
│   ├── overview-template.md          # Project overview template
│   ├── api-spec-template.md          # API specification template
│   ├── database-schema-template.md   # Database schema template
│   └── feature-spec-template.md      # Feature spec template
├── references/
│   └── spec-kit-conventions.md       # Complete style guide
└── scripts/
    └── validate-specs.py             # Validation automation
```

## Contributing

To improve this skill:
1. Test on real projects
2. Identify missing sections or common issues
3. Update templates in `assets/`
4. Enhance validation in `scripts/validate-specs.py`
5. Document patterns in `references/spec-kit-conventions.md`

## Version

**Version:** 1.0.0
**Last Updated:** 2025-02-02
**Author:** Spec-Kit Plus Team
