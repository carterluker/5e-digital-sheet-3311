interface FormFieldProps {
    id: string
    label: string
    type?: string
    autoComplete?: string
    minLength?: number
    maxLength?: number
    required?: boolean
    value: string
    onChange: (value: string) => void
}

function FormField({ id, label, type = 'text', autoComplete, minLength, maxLength, required = true, value, onChange }: FormFieldProps) {
    return (
        <div className="form-field">
            <label htmlFor={id}>{label}</label>
            <input
                id={id}
                name={id}
                type={type}
                autoComplete={autoComplete}
                minLength={minLength}
                maxLength={maxLength}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                required={required}
            />
        </div>
    )
}

export default FormField
