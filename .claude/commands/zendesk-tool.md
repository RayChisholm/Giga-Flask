# Create New Zendesk Tool

Generate complete boilerplate for a new Zendesk-integrated tool.

Tool name: $ARGUMENTS

## Instructions

1. **Gather Requirements**
   - Ask about the tool's purpose
   - Ask what Zendesk endpoints it needs
   - Ask what data it will display/manipulate
   - Ask about authentication requirements

2. **Create Route File**
   - Create `app/routes/tools/$TOOL_NAME.py`
   - Include Blueprint definition
   - Add basic routes (list, detail, create, edit)
   - Include proper error handling
   - Add authentication decorators

3. **Create Service Layer**
   - Create `app/services/$TOOL_NAME_service.py`
   - Implement business logic
   - Add proper error handling
   - Include logging

4. **Create Zendesk Integration**
   - Create or update `app/services/zendesk/$TOOL_NAME_zendesk.py`
   - Implement API calls with retry logic
   - Add rate limiting handling
   - Include caching where appropriate

5. **Create Models** (if needed)
   - Create SQLAlchemy model in `app/models/`
   - Add relationships
   - Create migration file

6. **Create Templates**
   - Create `app/templates/tools/$TOOL_NAME/` directory
   - Create list.html
   - Create detail.html
   - Create form.html (if needed)
   - Extend from base template
   - Include proper CSRF protection

7. **Create Tests**
   - Create `tests/test_$TOOL_NAME.py`
   - Add route tests
   - Add service tests
   - Add Zendesk integration tests (mocked)
   - Aim for 80%+ coverage

8. **Register Blueprint**
   - Add blueprint registration in `app/__init__.py`
   - Add to navigation in base template

9. **Documentation**
   - Add docstrings to all functions
   - Update README if needed
   - Add usage examples

10. **Verification**
    - Run test suite
    - Run linting
    - Manual testing in browser
    - Test error scenarios