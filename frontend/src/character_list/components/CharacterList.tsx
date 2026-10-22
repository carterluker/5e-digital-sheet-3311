import CharacterListItem, { type CharacterSummary } from './CharacterListItem.tsx'

function CharacterList({ characters }: { characters: CharacterSummary[] }) {
    if (characters.length === 0) {
        return <p>You don't have any characters yet.</p>
    }
    return (
        <ul className="character-list">
            {characters.map((character) => (
                <CharacterListItem key={character.id} character={character} />
            ))}
        </ul>
    )
}

export default CharacterList
