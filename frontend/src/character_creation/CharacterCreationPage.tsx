import { useState } from 'react'
import { Link } from 'react-router'

import FormError from '../login/components/FormError.tsx'
import FormField from '../login/components/FormField.tsx'

import SelectField, { type SelectOption } from './components/SelectField.tsx'
import { useModelList } from './useModelList.ts'

import './character_creation.css'

function CharacterCreationPage() {
    const [name, setName] = useState('')
    const [alignment, setAlignment] = useState('')
    const [speciesId, setSpeciesId] = useState('')
    const [classId, setClassId] = useState('')
    const [subclassId, setSubclassId] = useState('')
    const [backgroundId, setBackgroundId] = useState('')

    const species = useModelList<SelectOption>('/api/model/species/')
    const classes = useModelList<SelectOption>('/api/model/class/')
    const subclasses = useModelList<SelectOption>(classId ? `/api/model/subclass/?class_id=${classId}` : null)
    const backgrounds = useModelList<SelectOption>('/api/model/background/')

    const error = species.error ?? classes.error ?? subclasses.error ?? backgrounds.error

    // Subclasses belong to a class, so changing the class clears the subclass.
    function handleClassChange(value: string) {
        setClassId(value)
        setSubclassId('')
    }

    return (
        <main>
            <div className="character-creation">
                <h2>Create a character</h2>
                <form onSubmit={(e) => e.preventDefault()}>
                    <FormField id="name" label="Name" maxLength={255} value={name} onChange={setName} />
                    <FormField id="alignment" label="Alignment" maxLength={50} required={false} value={alignment} onChange={setAlignment} />
                    <SelectField id="species" label="Species" options={species.items} value={speciesId} onChange={setSpeciesId} />
                    <SelectField id="class" label="Class" options={classes.items} value={classId} onChange={handleClassChange} />
                    <SelectField
                        id="subclass"
                        label="Subclass"
                        options={subclasses.items}
                        placeholder={classId ? 'Select...' : 'Select a class first'}
                        disabled={!classId}
                        value={subclassId}
                        onChange={setSubclassId}
                    />
                    <SelectField id="background" label="Background" options={backgrounds.items} value={backgroundId} onChange={setBackgroundId} />
                    <FormError message={error} />
                    <Link to="/characters" className="button">Back to characters</Link>
                </form>
            </div>
        </main>
    )
}

export default CharacterCreationPage
