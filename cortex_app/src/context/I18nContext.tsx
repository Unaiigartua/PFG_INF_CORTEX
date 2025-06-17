import { createContext, useState, useContext, useEffect, ReactNode } from "react";

type Language = 'es' | 'en';

// Diccionario de traducciones
const translations = {
  es: {
    // Header
    'header.login': 'Iniciar Sesión',
    'header.logout': 'Salir',
    'header.close_session': 'Cerrar sesión',
    
    // Login Modal
    'login.title': 'Iniciar sesión',
    'login.register_title': 'Registro de usuario',
    'login.email': 'Email',
    'login.password': 'Contraseña',
    'login.email_placeholder': 'tu@email.com',
    'login.password_placeholder': '••••••••',
    'login.loading': 'Cargando...',
    'login.register': 'Registrarse',
    'login.login': 'Iniciar sesión',
    'login.register_success': '¡Registro exitoso! Ahora puedes iniciar sesión',
    'login.login_success': '¡Login exitoso!',
    'login.toggle_register': '¿No tienes cuenta? Regístrate',
    'login.toggle_login': '¿Ya tienes cuenta? Inicia sesión',
    'login.invalid_credentials': 'Credenciales inválidas',
    'login.registration_error': 'Error al registrarse',
    'login.auth_error': 'Error en la autenticación',
    
    // Message Input
    'input.placeholder': 'Escriba su consulta...',
    'input.send': 'ENVIAR',
    'input.reset': 'REINICIAR',
    'input.confirm_terms': 'Confirme todos los términos resaltados',
    'input.executing_query': 'Ejecutando consulta SQL...',
    'input.extracting_terms': 'Extrayendo términos...',
    'input.save_query_login': 'Inicia sesión para guardar tu consulta',
    'input.end_edit': 'Finalizar',
    'input.edit': 'Editar',
    'input.select_edit': 'Seleccionado',
    'input.add_term': 'Añadir término',
    'input.delete_term': 'Click para eliminar término',
    'input.generate_sql': 'Generando SQL...',
    
    // Examples
    'examples.title': 'Ejemplos',
    'examples.female_breast_cancer': 'Encuentra pacientes femeninas con cáncer de mama metastásico que tuvieron mastectomía en el último año',
    'examples.paget_disease': 'Pacientes femeninas diagnosticadas con enfermedad de Paget',
    'examples.adenosquamous_carcinoma': 'Pacientes femeninas diagnosticadas con carcinoma adenoescamoso de pulmón',
    'examples.lumpectomy': 'Pacientes diagnosticadas en el cuadrante interior inferior del seno que se sometieron a lumpectomía',
    
    // History
    'history.title': 'Historial de consultas',
    'history.view_history': 'Ver historial',
    'history.login_required': 'Inicia sesión para ver historial',
    'history.no_queries': 'No hay consultas en el historial',
    'history.login_message': 'Inicia sesión para ver tu historial de consultas',
    'history.details': 'Detalles',
    'history.delete': 'Eliminar',
    'history.confirm_delete': '¿Estás seguro de que quieres eliminar esta consulta?',
    'history.executable': 'Ejecutable',
    'history.not_executable': 'No ejecutable',
    'history.attempts': 'intentos',
    'history.attempt': 'intento',
    'history.query_details': 'Detalles de la consulta',
    'history.original_question': 'Pregunta original',
    'history.medical_terms': 'Términos médicos validados',
    'history.generated_sql': 'SQL generado',
    'history.status': 'Estado',
    'history.attempts_count': 'Intentos',
    'history.processing_time': 'Tiempo',
    'history.results_count': 'Resultados',
    'history.error_message': 'Error',
    'history.seconds': 's',
    'history.loading_details': 'Cargando detalles...',
    'history.error_loading': 'Error cargando historial',
    'history.error_deleting': 'Error eliminando consulta',
    
    // Term Validation Modal
    'term_validation.title': 'Validar Término',
    'term_validation.cancel': 'Cancelar',
    'term_validation.confirm': 'Confirmar selección',
    'term_validation.loading': 'Cargando...',
    'term_validation.previous': 'Anterior',
    'term_validation.next': 'Siguiente',
    'term_validation.of': 'de',
    'term_validation.error': 'Error al obtener términos similares',
    
    // Footer
    'footer.disclaimer': 'Disclaimer: Esta herramienta es una prueba y los resultados pueden no ser correctos',
    
    // Theme
    'theme.light': 'Cambiar a modo claro',
    'theme.dark': 'Cambiar a modo oscuro',
    
    // Logo
    'logo.description': 'Clinical Oriented Request Translator for EXecutable SQL',
    
    // General
    'general.loading': 'Cargando...',
    'general.error': 'Error',
    'general.success': 'Éxito',
    'general.cancel': 'Cancelar',
    'general.confirm': 'Confirmar',
    'general.close': 'Cerrar',

    // SQL Result View
    'sql_result.new_query': 'Nueva',
    'sql_result.check_sql': 'Comprobar',
    'sql_result.validating': 'Validando...',
    'sql_result.valid_executable': 'SQL Válido y Ejecutable',
    'sql_result.valid_not_executable': 'SQL Válido pero No Ejecutable',
    'sql_result.invalid': 'SQL Inválido',
    'sql_result.executable_original': 'SQL Ejecutable (original)',
    'sql_result.not_executable_original': 'SQL No Ejecutable (original)',
    'sql_result.view_error_details': 'Ver detalles del error',
    'sql_result.validation_info': 'Información de validación',
    'sql_result.valid_syntax': 'Sintaxis válida',
    'sql_result.executable': 'Ejecutable',
    'sql_result.time': 'Tiempo',
    'sql_result.rows': 'Filas',
    'sql_result.similar_example': 'Ejemplo similar utilizado en generación',
    'sql_result.yes': 'Sí',
    'sql_result.no': 'No',
  },
  
  en: {
    // Header
    'header.login': 'Sign In',
    'header.logout': 'Sign Out',
    'header.close_session': 'Sign Out',
    
    // Login Modal
    'login.title': 'Sign In',
    'login.register_title': 'User Registration',
    'login.email': 'Email',
    'login.password': 'Password',
    'login.email_placeholder': 'your@email.com',
    'login.password_placeholder': '••••••••',
    'login.loading': 'Loading...',
    'login.register': 'Register',
    'login.login': 'Sign In',
    'login.register_success': 'Registration successful! You can now sign in',
    'login.login_success': 'Login successful!',
    'login.toggle_register': "Don't have an account? Register",
    'login.toggle_login': 'Already have an account? Sign in',
    'login.invalid_credentials': 'Invalid credentials',
    'login.registration_error': 'Registration error',
    'login.auth_error': 'Authentication error',
  
    
    // Message Input
    'input.placeholder': 'Write your query...',
    'input.send': 'SEND',
    'input.reset': 'RESET',
    'input.confirm_terms': 'Confirm all highlighted terms',
    'input.executing_query': 'Executing SQL query...',
    'input.extracting_terms': 'Extracting terms...',
    'input.save_query_login': 'Sign in to save your query',
    'input.end_edit': 'Finish',
    'input.edit': 'Edit',
    'input.select_edit': 'Selected',
    'input.add_term': 'Add term',
    'input.delete_term': 'Click to delete term',
    'input.generate_sql': 'Generating SQL...',


    
    // Examples
    'examples.title': 'Examples',
    'examples.female_breast_cancer': 'Find female patients with metastatic breast cancer who had mastectomy in the past year',
    'examples.paget_disease': 'Female patients diagnosed with a paget disease',
    'examples.adenosquamous_carcinoma': 'Female patients diagnosed with adenosquamous carcinoma of the lung',
    'examples.lumpectomy': 'Patients diagnosed in the lower inner quadrant of breast that went under lumpectomy',
    
    // History
    'history.title': 'Query History',
    'history.view_history': 'View history',
    'history.login_required': 'Sign in to view history',
    'history.no_queries': 'No queries in history',
    'history.login_message': 'Sign in to view your query history',
    'history.details': 'Details',
    'history.delete': 'Delete',
    'history.confirm_delete': 'Are you sure you want to delete this query?',
    'history.executable': 'Executable',
    'history.not_executable': 'Not executable',
    'history.attempts': 'attempts',
    'history.attempt': 'attempt',
    'history.query_details': 'Query details',
    'history.original_question': 'Original question',
    'history.medical_terms': 'Validated medical terms',
    'history.generated_sql': 'Generated SQL',
    'history.status': 'Status',
    'history.attempts_count': 'Attempts',
    'history.processing_time': 'Processing time',
    'history.results_count': 'Results',
    'history.error_message': 'Error',
    'history.seconds': 's',
    'history.loading_details': 'Loading details...',
    'history.error_loading': 'Error loading history',
    'history.error_deleting': 'Error deleting query',
    
    // Term Validation Modal
    'term_validation.title': 'Validate Term',
    'term_validation.cancel': 'Cancel',
    'term_validation.confirm': 'Confirm Selection',
    'term_validation.loading': 'Loading...',
    'term_validation.previous': 'Previous',
    'term_validation.next': 'Next',
    'term_validation.of': 'of',
    'term_validation.error': 'Error fetching similar terms',
    
    // Footer
    'footer.disclaimer': 'Disclaimer: This tool is a test and results may not be correct',
    
    // Theme
    'theme.light': 'Switch to light mode',
    'theme.dark': 'Switch to dark mode',
    
    // Logo
    'logo.description': 'Clinical Oriented Request Translator for EXecutable SQL',
    
    // General
    'general.loading': 'Loading...',
    'general.error': 'Error',
    'general.success': 'Success',
    'general.cancel': 'Cancel',
    'general.confirm': 'Confirm',
    'general.close': 'Close',

    // SQL Result View
    'sql_result.new_query': 'New',
    'sql_result.check_sql': 'Check',
    'sql_result.validating': 'Validating...',
    'sql_result.valid_executable': 'Valid and Executable SQL',
    'sql_result.valid_not_executable': 'Valid but Non-Executable SQL',
    'sql_result.invalid': 'Invalid SQL',
    'sql_result.executable_original': 'Executable SQL (original)',
    'sql_result.not_executable_original': 'Non-Executable SQL (original)',
    'sql_result.view_error_details': 'View error details',
    'sql_result.validation_info': 'Validation information',
    'sql_result.valid_syntax': 'Valid syntax',
    'sql_result.executable': 'Executable',
    'sql_result.time': 'Time',
    'sql_result.rows': 'Rows',
    'sql_result.similar_example': 'Similar example used in generation',
    'sql_result.yes': 'Yes',
    'sql_result.no': 'No',
  }
} as const;

// Tipos derivados de las traducciones
type TranslationKeys = keyof typeof translations['es'];

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKeys) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>('es');

  // Cargar idioma desde localStorage al iniciar
  useEffect(() => {
    try {
      const savedLanguage = localStorage.getItem('language') as Language;
      if (savedLanguage && (savedLanguage === 'es' || savedLanguage === 'en')) {
        setLanguageState(savedLanguage);
        return;
      }
    } catch (e) {
      console.log('localStorage no disponible');
    }

    // Si no hay idioma guardado, detectar del navegador
    const browserLanguage = navigator.language;
    const detectedLanguage = browserLanguage.startsWith('es') ? 'es' : 'en';
    setLanguageState(detectedLanguage);
  }, []);

  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    try {
      localStorage.setItem('language', newLanguage);
    } catch (e) {
      console.log('No se pudo guardar el idioma en localStorage');
    }
  };

  // Función de traducción
  const t = (key: TranslationKeys): string => {
    const translation = translations[language][key];
    if (!translation) {
      console.warn(`Missing translation for key: ${key} in language: ${language}`);
      return key; // Devolver la clave si no hay traducción
    }
    return translation;
  };

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
}