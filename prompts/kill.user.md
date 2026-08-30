MODULE_IMPORT_NAME: {{MODULE_NAME}}

The module under test:

```python
{{MODULE_SOURCE}}
```

The suite as it stands, which already passes and already kills
{{KILLED}} of {{TOTAL}} mutants:

```python
{{TEST_SOURCE}}
```

These {{N_SURVIVORS}} changes were made to the module and the suite above did
not notice any of them:

{{SURVIVORS}}

Write new tests that catch as many of these as you can.
